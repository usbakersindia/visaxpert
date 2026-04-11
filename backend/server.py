from fastapi import FastAPI, APIRouter, HTTPException, Query, Header, Depends, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
import os
import logging
import hashlib
import hmac
import secrets
import asyncio
from pathlib import Path
from pydantic import BaseModel, Field, field_validator, EmailStr
from typing import Optional, List, Any
import uuid
from datetime import datetime, timezone, timedelta
import re
import httpx
from motor.motor_asyncio import AsyncIOMotorClient
import json
import resend

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Environment variables
GOOGLE_SHEET_WEBHOOK = os.environ.get('GOOGLE_SHEET_WEBHOOK', '')
RESEND_API_KEY = os.environ.get('RESEND_API_KEY', '')
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'info@visaxpertinternational.co.in')

# WhatsApp Business API credentials
WHATSAPP_ACCESS_TOKEN = os.environ.get('WHATSAPP_ACCESS_TOKEN', '')
WHATSAPP_PHONE_NUMBER_ID = os.environ.get('WHATSAPP_PHONE_NUMBER_ID', '1021627281029893')
WHATSAPP_TEMPLATE_NAME = os.environ.get('WHATSAPP_TEMPLATE_NAME', 'crmall')

# Initialize Resend
if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'visaxpert')

# Dashboard credentials - Multiple users with different access
DASHBOARD_USERS = {
    "sunilarora@visaxpert.co": {
        "password": "VisaXpert@2024",
        "name": "Sunil Arora",
        "access": "main_landing",  # Can see leads from main landing page
        "sources": ["website", "meta_ads", "google_sheets", "manual", "ivr_missed_call"]  # Includes IVR leads
    },
    "navyaarora@visaxpert.co": {
        "password": "VisaXpert@2024",
        "name": "Navya Arora", 
        "access": "university_change",  # Can see leads from university change page
        "sources": ["university_change"]
    },
    "admin@visaxpert.com": {
        "password": "VisaXpert@2024",
        "name": "Admin",
        "access": "all",  # Can see all leads
        "sources": []  # Empty means all sources
    }
}

# Legacy credentials (kept for backward compatibility)
DASHBOARD_EMAIL = os.environ.get('DASHBOARD_EMAIL', 'admin@visaxpert.com')
DASHBOARD_PASSWORD = os.environ.get('DASHBOARD_PASSWORD', 'VisaXpert@2024')

# Facebook App credentials (for webhook verification)
FB_APP_SECRET = os.environ.get('FB_APP_SECRET', '')
FB_VERIFY_TOKEN = os.environ.get('FB_VERIFY_TOKEN', 'visaxpert_verify_token_2024')

# Google Sheets Auto-Sync (for importer)
GOOGLE_SHEETS_ID = os.environ.get('GOOGLE_SHEETS_ID', '')
GOOGLE_SHEETS_RANGE = os.environ.get('GOOGLE_SHEETS_RANGE', 'Sheet1!A:G')
GOOGLE_SHEETS_SYNC_URL = os.environ.get('GOOGLE_SHEETS_SYNC_URL', '')

# MongoDB client
mongo_client: AsyncIOMotorClient = None
db = None

# Create the main app
app = FastAPI(title="VisaXpert API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ==================== MODELS ====================

class EnquiryCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., min_length=5, max_length=100)
    phone: str = Field(..., min_length=10, max_length=10)
    city: str = Field(..., min_length=2, max_length=100)
    country_of_interest: str
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', v):
            raise ValueError('Please enter a valid email address')
        return v
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        if not re.match(r'^[6-9]\d{9}$', v):
            raise ValueError('Please enter a valid 10-digit Indian mobile number')
        return v
    
    @field_validator('country_of_interest')
    @classmethod
    def validate_country(cls, v):
        if not v or len(v.strip()) < 2:
            raise ValueError('Please enter a valid country name')
        return v


class EnquiryResponse(BaseModel):
    id: str
    name: str
    email: str
    phone: str
    city: str
    country_of_interest: str
    created_at: str
    status: str


# Webhook Lead Model - Flexible for Meta/Google Ads
class WebhookLead(BaseModel):
    name: Optional[str] = None
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    phone_number: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    country_of_interest: Optional[str] = None
    source: Optional[str] = "webhook"
    campaign: Optional[str] = None
    ad_name: Optional[str] = None
    form_name: Optional[str] = None
    platform: Optional[str] = None
    
    class Config:
        extra = "allow"


class LeadResponse(BaseModel):
    id: str
    name: str
    email: str
    phone: str
    city: str
    country: str
    source: str
    status: str
    created_at: str
    campaign: Optional[str] = None
    platform: Optional[str] = None
    extra_data: Optional[dict] = None


class LeadsListResponse(BaseModel):
    leads: List[LeadResponse]
    total: int
    page: int
    per_page: int


class DashboardStats(BaseModel):
    total_leads: int
    today_leads: int
    website_leads: int
    meta_leads: int
    google_leads: int
    other_leads: int
    new_leads: int
    contacted_leads: int
    converted_leads: int


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    success: bool
    message: str
    token: Optional[str] = None


class ImportResult(BaseModel):
    success: bool
    imported: int
    skipped: int
    message: str


class SyncSettings(BaseModel):
    google_sheets_url: Optional[str] = None
    auto_sync_enabled: bool = False
    sync_interval_minutes: int = 30
    last_sync: Optional[str] = None


# ==================== DATABASE ====================

async def get_database():
    return db


async def startup_db_client():
    global mongo_client, db
    try:
        mongo_client = AsyncIOMotorClient(MONGO_URL)
        db = mongo_client[DB_NAME]
        await mongo_client.admin.command('ping')
        logger.info("Connected to MongoDB successfully")
        
        # Create indexes
        await db.leads.create_index("created_at")
        await db.leads.create_index("source")
        await db.leads.create_index("email")
        await db.leads.create_index([("email", 1), ("phone", 1), ("created_at", -1)])
        
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise


async def shutdown_db_client():
    global mongo_client
    if mongo_client:
        mongo_client.close()
        logger.info("MongoDB connection closed")


# ==================== AUTH HELPERS ====================

def generate_token(email: str) -> str:
    """Generate a simple session token"""
    timestamp = datetime.now(timezone.utc).isoformat()
    data = f"{email}:{timestamp}:{secrets.token_hex(16)}"
    return hashlib.sha256(data.encode()).hexdigest()


def verify_credentials(email: str, password: str) -> dict:
    """Verify email and password, returns user info if valid"""
    email_lower = email.lower()
    if email_lower in DASHBOARD_USERS:
        user = DASHBOARD_USERS[email_lower]
        if user["password"] == password:
            return {
                "valid": True,
                "email": email_lower,
                "name": user["name"],
                "access": user["access"],
                "sources": user["sources"]
            }
    # Legacy check
    if email_lower == DASHBOARD_EMAIL.lower() and password == DASHBOARD_PASSWORD:
        return {
            "valid": True,
            "email": email_lower,
            "name": "Admin",
            "access": "all",
            "sources": []
        }
    return {"valid": False}


def verify_auth(email: str = Query(...), password: str = Query(...)) -> dict:
    """Verify authentication via query params, returns user info"""
    user_info = verify_credentials(email, password)
    if not user_info["valid"]:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return user_info


def get_source_filter(user_info: dict) -> dict:
    """Get MongoDB filter based on user's access level"""
    if user_info["access"] == "all" or not user_info["sources"]:
        return {}  # No filter, show all
    
    if user_info["access"] == "university_change":
        return {"source": "university_change"}
    
    if user_info["access"] == "main_landing":
        # Show everything except university_change
        return {"source": {"$ne": "university_change"}}


# ==================== HELPER FUNCTIONS ====================

async def send_to_google_sheets(enquiry_data: dict) -> bool:
    if not GOOGLE_SHEET_WEBHOOK:
        logger.warning("Google Sheets webhook not configured!")
        return False
    
    try:
        async with httpx.AsyncClient(follow_redirects=True) as http_client:
            response = await http_client.post(
                GOOGLE_SHEET_WEBHOOK,
                json=enquiry_data,
                timeout=15.0
            )
            if response.status_code == 200:
                logger.info(f"Successfully sent enquiry to Google Sheets: {enquiry_data.get('name', 'Unknown')}")
                return True
            else:
                logger.warning(f"Google Sheets response: {response.status_code}")
                return False
    except Exception as e:
        logger.error(f"Failed to send to Google Sheets: {str(e)}")
        return False


async def save_lead_to_db(lead_data: dict) -> str:
    """Save a lead to MongoDB and return the ID"""
    try:
        lead_id = str(uuid.uuid4())
        lead_doc = {
            "lead_id": lead_id,
            "name": lead_data.get("name", ""),
            "email": lead_data.get("email", ""),
            "phone": lead_data.get("phone", ""),
            "city": lead_data.get("city", ""),
            "country": lead_data.get("country", ""),
            "source": lead_data.get("source", "website"),
            "status": "new",
            "campaign": lead_data.get("campaign"),
            "platform": lead_data.get("platform"),
            "extra_data": lead_data.get("extra_data", {}),
            "created_at": datetime.now(timezone.utc),
        }
        
        await db.leads.insert_one(lead_doc)
        logger.info(f"Saved lead to database: {lead_id} from {lead_data.get('source', 'website')}")
        return lead_id
    except Exception as e:
        logger.error(f"Failed to save lead to database: {e}")
        raise


async def check_duplicate_lead(email: str, phone: str, hours: int = 24) -> bool:
    """Check if a lead with same email/phone exists in last N hours"""
    if not email and not phone:
        return False
    
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    query = {
        "created_at": {"$gte": cutoff},
        "$or": []
    }
    
    if email:
        query["$or"].append({"email": email})
    if phone:
        query["$or"].append({"phone": phone})
    
    if not query["$or"]:
        return False
    
    existing = await db.leads.find_one(query)
    return existing is not None


async def send_university_change_welcome_email(name: str, email: str):
    """Send welcome email to university change leads"""
    if not RESEND_API_KEY or not email:
        logger.warning("Resend API key not configured or no email provided, skipping welcome email")
        return False
    
    try:
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #10b981;">Dear {name or 'Student'},</h2>
            
            <p>Thank you for choosing <strong>Visaxpert Berlin</strong>.</p>
            
            <p>We have successfully received your request and our team will contact you shortly to identify the most suitable university and course transition options for you.</p>
            
            <p>At Visaxpert Berlin, we not only guide you through the process but also ensure that you receive some of the most competitive service rates in the market, along with exclusive university discounts that we are able to offer through our partnerships.</p>
            
            <p>One of our consultants will be reaching out to you shortly to guide you through the next steps.</p>
            
            <p>Until then, feel free to reply to this email or reach out to us at <strong>+49 1577 4493633</strong> or visit our office in Berlin with prior appointment.</p>
            
            <p>We look forward to assisting you.</p>
            
            <p style="margin-top: 30px;">
                Warm regards,<br>
                <strong>Team Visaxpert Berlin</strong>
            </p>
            
            <hr style="margin-top: 30px; border: none; border-top: 1px solid #e5e7eb;">
            <p style="font-size: 12px; color: #6b7280;">
                Visaxpert Berlin | Alfred Jung Strasse 12, 529, Berlin, Germany<br>
                Website: <a href="https://visaxpertinternational.co.in/university-change" style="color: #10b981;">visaxpertinternational.co.in</a>
            </p>
        </div>
        """
        
        params = {
            "from": SENDER_EMAIL,
            "to": [email],
            "subject": "Thank You for Contacting Visaxpert Berlin - Your University Transfer Inquiry",
            "html": html_content
        }
        
        # Run sync SDK in thread to keep FastAPI non-blocking
        result = await asyncio.to_thread(resend.Emails.send, params)
        logger.info(f"Welcome email sent to {email}, email_id: {result.get('id')}")
        return True
    except Exception as e:
        logger.error(f"Failed to send welcome email to {email}: {str(e)}")
        return False


async def send_whatsapp_template_message(phone: str, name: str):
    """Send WhatsApp template message to leads (not university_change)"""
    if not WHATSAPP_ACCESS_TOKEN or not phone:
        logger.warning("WhatsApp access token not configured or no phone provided, skipping WhatsApp message")
        return False
    
    # Format phone number - ensure it starts with country code
    formatted_phone = phone.replace(" ", "").replace("-", "").replace("+", "")
    if not formatted_phone.startswith("91") and len(formatted_phone) == 10:
        formatted_phone = "91" + formatted_phone
    
    try:
        # Using custom WhatsApp CRM API
        url = f"https://wacrm.nirvachanguru.com/api/meta/v19.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
        
        headers = {
            "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "to": formatted_phone,
            "type": "template",
            "template": {
                "name": WHATSAPP_TEMPLATE_NAME,
                "language": {"code": "en"}
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"WhatsApp message sent to {formatted_phone}, queue_id: {result.get('message', {}).get('queue_id')}")
                return True
            else:
                logger.error(f"Failed to send WhatsApp message to {formatted_phone}: {response.status_code} - {response.text}")
                return False
                
    except Exception as e:
        logger.error(f"Failed to send WhatsApp message to {formatted_phone}: {str(e)}")
        return False


# ==================== API ENDPOINTS ====================

@api_router.get("/")
async def root():
    return {"message": "VisaXpert API", "status": "running"}


@api_router.get("/health")
async def health_check():
    db_status = "connected" if db is not None else "disconnected"
    return {
        "status": "healthy",
        "sheets_configured": bool(GOOGLE_SHEET_WEBHOOK),
        "database": db_status,
        "facebook_configured": bool(FB_APP_SECRET)
    }


# Website Form Submission
@api_router.post("/enquiry", response_model=EnquiryResponse)
async def create_enquiry(input: EnquiryCreate):
    created_at = datetime.now(timezone.utc).isoformat()
    
    lead_data = {
        "name": input.name,
        "email": input.email,
        "phone": input.phone,
        "city": input.city,
        "country": input.country_of_interest,
        "source": "website",
        "platform": "website"
    }
    
    try:
        lead_id = await save_lead_to_db(lead_data)
    except Exception as e:
        logger.error(f"Database error: {e}")
        lead_id = str(uuid.uuid4())
    
    # Also send to Google Sheets
    sheets_data = {
        "name": input.name,
        "email": input.email,
        "phone": input.phone,
        "city": input.city,
        "country": input.country_of_interest,
        "date": created_at,
        "source": "website"
    }
    await send_to_google_sheets(sheets_data)
    
    return EnquiryResponse(
        id=lead_id,
        name=input.name,
        email=input.email,
        phone=input.phone,
        city=input.city,
        country_of_interest=input.country_of_interest,
        created_at=created_at,
        status="submitted"
    )


# ==================== UNIVERSAL WEBHOOK ====================

@api_router.post("/webhook/lead")
async def receive_webhook_lead(lead: WebhookLead):
    """Universal webhook for any lead source"""
    name = lead.name or lead.full_name or ""
    phone = lead.phone or lead.phone_number or ""
    country = lead.country or lead.country_of_interest or ""
    
    source = lead.source or "webhook"
    if lead.platform:
        if "facebook" in lead.platform.lower() or "instagram" in lead.platform.lower():
            source = "meta"
        elif "google" in lead.platform.lower():
            source = "google"
    
    extra_data = {}
    lead_dict = lead.model_dump()
    standard_fields = {'name', 'full_name', 'email', 'phone', 'phone_number', 'city', 'country', 'country_of_interest', 'source', 'campaign', 'ad_name', 'form_name', 'platform'}
    for key, value in lead_dict.items():
        if key not in standard_fields and value is not None:
            extra_data[key] = value
    
    lead_data = {
        "name": name,
        "email": lead.email or "",
        "phone": phone,
        "city": lead.city or "",
        "country": country,
        "source": source,
        "campaign": lead.campaign or lead.ad_name or lead.form_name,
        "platform": lead.platform,
        "extra_data": extra_data if extra_data else None
    }
    
    try:
        lead_id = await save_lead_to_db(lead_data)
    except Exception as e:
        logger.error(f"Failed to save webhook lead: {e}")
        raise HTTPException(status_code=500, detail="Failed to save lead")
    
    # Send welcome email for university_change leads
    if source == "university_change" and lead.email:
        asyncio.create_task(send_university_change_welcome_email(name, lead.email))
    
    # Send WhatsApp message for all leads EXCEPT university_change
    if source != "university_change" and phone:
        asyncio.create_task(send_whatsapp_template_message(phone, name))
    
    # Also send to Google Sheets
    sheets_data = {
        "name": name,
        "email": lead.email or "",
        "phone": phone,
        "city": lead.city or "",
        "country": country,
        "date": datetime.now(timezone.utc).isoformat(),
        "source": source
    }
    await send_to_google_sheets(sheets_data)
    
    return {"success": True, "lead_id": lead_id, "message": "Lead received successfully"}


# ==================== IVR MISSED CALL WEBHOOK ====================

@api_router.get("/webhook/ivr")
async def receive_ivr_webhook_get(request: Request):
    """
    Webhook endpoint for IVR/Missed Call service (GET method with query params)
    Accepts leads from missed call panels like c2c.techmet.in / waflb.nirvachanguru.com
    
    Expected query params:
    - SourceNumber: Caller's phone number
    - DestinationNumber: Desk phone number
    - CallDuration: Duration in seconds
    - Status: cancel-customer, cancel-Agent, answered, etc.
    - StartTime, EndTime: Call timestamps
    - Direction: IVR
    - receiver_name: Agent/Branch name
    - CallRecordingUrl: Recording URL if available
    """
    try:
        # Get all query parameters
        params = dict(request.query_params)
        
        logger.info(f"IVR webhook received (GET): {json.dumps(params, indent=2)}")
        
        # Extract phone number (SourceNumber is the caller)
        phone = params.get('SourceNumber') or params.get('source_number') or params.get('caller') or ""
        
        # Clean phone number - remove country code if present
        if phone:
            phone = re.sub(r'[^\d]', '', str(phone))  # Remove non-digits
            if phone.startswith('91') and len(phone) > 10:
                phone = phone[2:]  # Remove 91 prefix
            if phone.startswith('0') and len(phone) > 10:
                phone = phone[1:]  # Remove leading 0
        
        # Extract other fields
        dest_number = params.get('DestinationNumber') or ""
        call_duration = params.get('CallDuration') or params.get('TalkDuration') or "0"
        status = params.get('Status') or "missed"
        start_time = params.get('StartTime') or ""
        end_time = params.get('EndTime') or ""
        direction = params.get('Direction') or "IVR"
        receiver_name = params.get('receiver_name') or params.get('DialWhomNumber') or ""
        call_recording = params.get('CallRecordingUrl') or ""
        call_sid = params.get('CallSid') or ""
        call_group = params.get('call_group') or ""
        key_press = params.get('key_press') or ""
        
        # Build extra data with all received fields
        extra_data = {
            "destination_number": dest_number,
            "call_duration": call_duration,
            "talk_duration": params.get('TalkDuration') or "0",
            "status": status,
            "start_time": start_time,
            "end_time": end_time,
            "direction": direction,
            "receiver_name": receiver_name,
            "call_recording_url": call_recording,
            "call_sid": call_sid,
            "call_group": call_group,
            "key_press": key_press,
            "coins": params.get('coins') or "",
            "campaign_id": params.get('campid') or "",
            "client_id": params.get('client_id') or "",
            "raw_params": params  # Store complete original params
        }
        
        # Determine branch from receiver_name or destination number
        branch = receiver_name or ""
        if not branch and dest_number:
            # Map destination numbers to branches if known
            branch = f"Desk: {dest_number[-10:]}" if dest_number else ""
        
        # Create lead data
        lead_data = {
            "name": f"IVR Call - {phone[-4:] if phone else 'Unknown'}",
            "email": "",
            "phone": phone,
            "city": branch or "IVR Call",
            "country": "India",
            "source": "ivr_missed_call",
            "campaign": f"IVR - {status}",
            "platform": "techmet_ivr",
            "extra_data": extra_data
        }
        
        # Check if phone number exists
        if not phone:
            logger.warning("IVR webhook received without phone number")
            return {"success": False, "message": "SourceNumber is required"}
        
        # Save to database
        try:
            lead_id = await save_lead_to_db(lead_data)
            logger.info(f"IVR lead saved successfully: {lead_id}, phone: {phone}, status: {status}")
        except Exception as e:
            logger.error(f"Failed to save IVR lead: {e}")
            raise HTTPException(status_code=500, detail="Failed to save lead")
        
        # Send WhatsApp message for IVR leads (only for missed calls, not answered)
        if phone and status.lower() in ['cancel-customer', 'cancel-agent', 'missed', 'no-answer']:
            asyncio.create_task(send_whatsapp_template_message(phone, ""))
        
        # Send to Google Sheets
        sheets_data = {
            "name": lead_data["name"],
            "email": "",
            "phone": phone,
            "city": branch or "IVR",
            "country": "India",
            "date": start_time or datetime.now(timezone.utc).isoformat(),
            "source": f"ivr_missed_call ({status})"
        }
        await send_to_google_sheets(sheets_data)
        
        return {
            "success": True, 
            "lead_id": lead_id, 
            "message": "IVR lead received successfully",
            "phone": phone,
            "status": status
        }
        
    except Exception as e:
        logger.error(f"Error processing IVR webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/webhook/ivr")
async def receive_ivr_webhook_post(request: Request):
    """
    Webhook endpoint for IVR/Missed Call service (POST method)
    Accepts both JSON body and form data
    """
    try:
        # Try to parse as JSON first
        try:
            payload = await request.json()
        except Exception:
            # If not JSON, try form data
            form = await request.form()
            payload = dict(form)
        
        logger.info(f"IVR webhook received (POST): {json.dumps(payload, indent=2) if isinstance(payload, dict) else payload}")
        
        # Extract phone number (try multiple field names)
        phone = (
            payload.get('SourceNumber') or
            payload.get('source_number') or
            payload.get('caller') or 
            payload.get('phone') or 
            payload.get('phone_number') or 
            payload.get('caller_number') or 
            payload.get('mobile') or 
            ""
        )
        
        # Clean phone number
        if phone:
            phone = re.sub(r'[^\d]', '', str(phone))
            if phone.startswith('91') and len(phone) > 10:
                phone = phone[2:]
            if phone.startswith('0') and len(phone) > 10:
                phone = phone[1:]
        
        # Extract other fields
        status = payload.get('Status') or payload.get('status') or "missed"
        start_time = payload.get('StartTime') or payload.get('start_time') or ""
        receiver_name = payload.get('receiver_name') or payload.get('DialWhomNumber') or ""
        call_duration = payload.get('CallDuration') or payload.get('call_duration') or "0"
        
        # Build extra data
        extra_data = {
            "destination_number": payload.get('DestinationNumber') or "",
            "call_duration": call_duration,
            "status": status,
            "start_time": start_time,
            "end_time": payload.get('EndTime') or "",
            "direction": payload.get('Direction') or "IVR",
            "receiver_name": receiver_name,
            "call_recording_url": payload.get('CallRecordingUrl') or "",
            "call_sid": payload.get('CallSid') or "",
            "raw_payload": payload
        }
        
        branch = receiver_name or ""
        
        lead_data = {
            "name": f"IVR Call - {phone[-4:] if phone else 'Unknown'}",
            "email": "",
            "phone": phone,
            "city": branch or "IVR Call",
            "country": "India",
            "source": "ivr_missed_call",
            "campaign": f"IVR - {status}",
            "platform": "techmet_ivr",
            "extra_data": extra_data
        }
        
        if not phone:
            logger.warning("IVR webhook received without phone number")
            return {"success": False, "message": "Phone number is required"}
        
        try:
            lead_id = await save_lead_to_db(lead_data)
            logger.info(f"IVR lead saved successfully: {lead_id}, phone: {phone}, status: {status}")
        except Exception as e:
            logger.error(f"Failed to save IVR lead: {e}")
            raise HTTPException(status_code=500, detail="Failed to save lead")
        
        # Send WhatsApp for missed calls
        if phone and status.lower() in ['cancel-customer', 'cancel-agent', 'missed', 'no-answer']:
            asyncio.create_task(send_whatsapp_template_message(phone, ""))
        
        # Send to Google Sheets
        sheets_data = {
            "name": lead_data["name"],
            "email": "",
            "phone": phone,
            "city": branch or "IVR",
            "country": "India",
            "date": start_time or datetime.now(timezone.utc).isoformat(),
            "source": f"ivr_missed_call ({status})"
        }
        await send_to_google_sheets(sheets_data)
        
        return {
            "success": True, 
            "lead_id": lead_id, 
            "message": "IVR lead received successfully",
            "phone": phone,
            "status": status
        }
        
    except Exception as e:
        logger.error(f"Error processing IVR webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== FACEBOOK WEBHOOKS ====================

@api_router.get("/webhook/facebook")
async def facebook_webhook_verify(request: Request):
    """
    Facebook Webhook Verification Endpoint
    Facebook will send a GET request with hub.mode, hub.verify_token, and hub.challenge
    """
    params = dict(request.query_params)
    
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")
    
    logger.info(f"Facebook webhook verification: mode={mode}, token={token}")
    
    if mode == "subscribe" and token == FB_VERIFY_TOKEN:
        logger.info("Facebook webhook verified successfully!")
        return int(challenge)
    else:
        logger.warning(f"Facebook webhook verification failed. Expected token: {FB_VERIFY_TOKEN}")
        raise HTTPException(status_code=403, detail="Verification failed")


@api_router.post("/webhook/facebook")
async def facebook_webhook_receive(request: Request):
    """
    Receive leads from Facebook Lead Ads
    Facebook sends lead data in a specific format
    """
    try:
        body = await request.body()
        payload = await request.json()
        
        logger.info(f"Facebook webhook received: {json.dumps(payload, indent=2)}")
        
        # Verify signature if FB_APP_SECRET is configured
        if FB_APP_SECRET:
            signature = request.headers.get("X-Hub-Signature-256", "")
            if signature:
                expected_signature = "sha256=" + hmac.new(
                    FB_APP_SECRET.encode(),
                    body,
                    hashlib.sha256
                ).hexdigest()
                
                if not hmac.compare_digest(signature, expected_signature):
                    logger.warning("Invalid Facebook signature")
                    raise HTTPException(status_code=403, detail="Invalid signature")
        
        # Process the webhook payload
        leads_processed = 0
        
        if "entry" in payload:
            for entry in payload.get("entry", []):
                for change in entry.get("changes", []):
                    if change.get("field") == "leadgen":
                        leadgen_data = change.get("value", {})
                        
                        # Extract lead data
                        lead_data = {
                            "name": "",
                            "email": "",
                            "phone": "",
                            "city": "",
                            "country": "",
                            "source": "meta",
                            "platform": "facebook",
                            "campaign": leadgen_data.get("ad_name") or leadgen_data.get("form_name"),
                            "extra_data": {
                                "leadgen_id": leadgen_data.get("leadgen_id"),
                                "page_id": leadgen_data.get("page_id"),
                                "form_id": leadgen_data.get("form_id"),
                                "ad_id": leadgen_data.get("ad_id"),
                                "adgroup_id": leadgen_data.get("adgroup_id"),
                            }
                        }
                        
                        # Parse field_data if present
                        for field in leadgen_data.get("field_data", []):
                            field_name = field.get("name", "").lower()
                            field_values = field.get("values", [])
                            field_value = field_values[0] if field_values else ""
                            
                            if "name" in field_name or "full_name" in field_name:
                                lead_data["name"] = field_value
                            elif "email" in field_name:
                                lead_data["email"] = field_value
                            elif "phone" in field_name:
                                lead_data["phone"] = field_value
                            elif "city" in field_name:
                                lead_data["city"] = field_value
                            elif "country" in field_name:
                                lead_data["country"] = field_value
                        
                        # Save lead
                        try:
                            await save_lead_to_db(lead_data)
                            leads_processed += 1
                            
                            # Send to Google Sheets
                            sheets_data = {
                                "name": lead_data["name"],
                                "email": lead_data["email"],
                                "phone": lead_data["phone"],
                                "city": lead_data["city"],
                                "country": lead_data["country"],
                                "date": datetime.now(timezone.utc).isoformat(),
                                "source": "meta"
                            }
                            await send_to_google_sheets(sheets_data)
                            
                        except Exception as e:
                            logger.error(f"Failed to save Facebook lead: {e}")
        
        return {"success": True, "leads_processed": leads_processed}
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    except Exception as e:
        logger.error(f"Facebook webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== GOOGLE SHEETS IMPORTER ====================

@api_router.post("/webhook/google")
async def receive_google_lead(payload: dict = {}):
    """Webhook for Google Ads Lead Form Extensions"""
    lead_data = payload.get("lead_form_submission", payload)
    user_data = lead_data.get("user_column_data", [])
    
    field_map = {}
    for item in user_data:
        column_name = item.get("column_name", "").lower()
        value = item.get("string_value", "")
        field_map[column_name] = value
    
    data = {
        "name": field_map.get("full_name") or field_map.get("name") or lead_data.get("name", ""),
        "email": field_map.get("email") or lead_data.get("email", ""),
        "phone": field_map.get("phone_number") or field_map.get("phone") or lead_data.get("phone", ""),
        "city": field_map.get("city") or lead_data.get("city", ""),
        "country": field_map.get("country") or lead_data.get("country", ""),
        "source": "google",
        "campaign": lead_data.get("campaign_id") or lead_data.get("campaign"),
        "platform": "google_ads",
        "extra_data": payload
    }
    
    try:
        lead_id = await save_lead_to_db(data)
    except Exception as e:
        logger.error(f"Failed to save Google lead: {e}")
        raise HTTPException(status_code=500, detail="Failed to save lead")
    
    sheets_data = {
        "name": data["name"],
        "email": data["email"],
        "phone": data["phone"],
        "city": data["city"],
        "country": data["country"],
        "date": datetime.now(timezone.utc).isoformat(),
        "source": "google"
    }
    await send_to_google_sheets(sheets_data)
    
    return {"success": True, "lead_id": lead_id}


@api_router.post("/dashboard/import-sheets", response_model=ImportResult)
async def import_from_google_sheets(
    email: str = Query(...),
    password: str = Query(...),
    sheet_data: List[dict] = []
):
    """
    Import leads from Google Sheets data
    Accepts an array of lead objects from the frontend
    """
    if not verify_credentials(email, password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    imported = 0
    skipped = 0
    
    for row in sheet_data:
        try:
            # Normalize field names (handle different column headers)
            name = row.get("name") or row.get("Name") or row.get("Full Name") or ""
            lead_email = row.get("email") or row.get("Email") or ""
            phone = row.get("phone") or row.get("Phone") or row.get("Mobile") or ""
            city = row.get("city") or row.get("City") or ""
            country = row.get("country") or row.get("Country") or row.get("Country of Interest") or ""
            source = row.get("source") or row.get("Source") or "sheets_import"
            date_str = row.get("date") or row.get("Date") or row.get("Timestamp") or ""
            
            # Skip empty rows
            if not name and not lead_email and not phone:
                skipped += 1
                continue
            
            # Check for duplicates (by email or phone in last 30 days)
            is_duplicate = await check_duplicate_lead(lead_email, phone, hours=720)  # 30 days
            if is_duplicate:
                skipped += 1
                continue
            
            # Parse date if provided
            created_at = datetime.now(timezone.utc)
            if date_str:
                try:
                    # Try common date formats
                    for fmt in ["%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M:%S", "%d/%m/%Y", "%Y-%m-%d"]:
                        try:
                            created_at = datetime.strptime(date_str.split(".")[0], fmt)
                            if created_at.tzinfo is None:
                                created_at = created_at.replace(tzinfo=timezone.utc)
                            break
                        except ValueError:
                            continue
                except Exception:
                    pass
            
            # Save lead
            lead_doc = {
                "lead_id": str(uuid.uuid4()),
                "name": name,
                "email": lead_email,
                "phone": str(phone),
                "city": city,
                "country": country,
                "source": source if source != "sheets_import" else "google_sheets",
                "status": "new",
                "campaign": None,
                "platform": "sheets_import",
                "extra_data": {"imported_from": "google_sheets", "original_row": row},
                "created_at": created_at,
            }
            
            await db.leads.insert_one(lead_doc)
            imported += 1
            
        except Exception as e:
            logger.error(f"Failed to import row: {e}")
            skipped += 1
    
    return ImportResult(
        success=True,
        imported=imported,
        skipped=skipped,
        message=f"Imported {imported} leads, skipped {skipped} (duplicates or empty)"
    )


# ==================== GOOGLE SHEETS AUTO-SYNC ====================

async def fetch_google_sheet_csv(sheet_url: str) -> str:
    """Fetch Google Sheet as CSV using public export URL"""
    # Convert various Google Sheets URL formats to CSV export URL
    sheet_id = None
    
    if "/spreadsheets/d/" in sheet_url:
        # Extract sheet ID from URL
        parts = sheet_url.split("/spreadsheets/d/")
        if len(parts) > 1:
            sheet_id = parts[1].split("/")[0].split("?")[0]
    elif len(sheet_url) == 44 or (len(sheet_url) > 20 and "/" not in sheet_url):
        # Assume it's just the sheet ID
        sheet_id = sheet_url
    
    if not sheet_id:
        raise ValueError("Invalid Google Sheets URL or ID")
    
    # Public CSV export URL
    csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
    
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(csv_url, timeout=30.0)
            if response.status_code == 200:
                return response.text
            else:
                raise HTTPException(status_code=400, detail=f"Failed to fetch sheet: {response.status_code}")
    except httpx.TimeoutException:
        raise HTTPException(status_code=408, detail="Timeout fetching Google Sheet")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching sheet: {str(e)}")


def parse_csv_to_leads(csv_text: str) -> List[dict]:
    """Parse CSV text into lead dictionaries"""
    import csv
    from io import StringIO
    
    leads = []
    reader = csv.DictReader(StringIO(csv_text))
    
    for row in reader:
        # Normalize field names (case-insensitive matching)
        normalized = {}
        for key, value in row.items():
            if key:
                key_lower = key.lower().strip()
                normalized[key_lower] = value.strip() if value else ""
        
        # Map to lead fields
        lead = {
            "name": normalized.get("name") or normalized.get("full name") or normalized.get("full_name") or "",
            "email": normalized.get("email") or normalized.get("email address") or "",
            "phone": normalized.get("phone") or normalized.get("phone number") or normalized.get("mobile") or "",
            "city": normalized.get("city") or "",
            "country": normalized.get("country") or normalized.get("country of interest") or "",
            "source": normalized.get("source") or "google_sheets",
            "date": normalized.get("date") or normalized.get("timestamp") or normalized.get("submitted") or "",
        }
        
        # Only add if has at least name, email or phone
        if lead["name"] or lead["email"] or lead["phone"]:
            leads.append(lead)
    
    return leads


@api_router.get("/dashboard/sync-settings")
async def get_sync_settings(email: str = Query(...), password: str = Query(...)):
    """Get Google Sheets sync settings"""
    verify_auth(email, password)
    
    try:
        settings = await db.settings.find_one({"type": "google_sheets_sync"})
        if settings:
            return {
                "google_sheets_url": settings.get("google_sheets_url", ""),
                "auto_sync_enabled": settings.get("auto_sync_enabled", False),
                "sync_interval_minutes": settings.get("sync_interval_minutes", 30),
                "last_sync": settings.get("last_sync"),
                "last_sync_result": settings.get("last_sync_result")
            }
        return {
            "google_sheets_url": "",
            "auto_sync_enabled": False,
            "sync_interval_minutes": 30,
            "last_sync": None,
            "last_sync_result": None
        }
    except Exception as e:
        logger.error(f"Error getting sync settings: {e}")
        raise HTTPException(status_code=500, detail="Failed to get settings")


@api_router.post("/dashboard/sync-settings")
async def save_sync_settings(
    email: str = Query(...),
    password: str = Query(...),
    google_sheets_url: str = Query(""),
    auto_sync_enabled: bool = Query(False),
    sync_interval_minutes: int = Query(30)
):
    """Save Google Sheets sync settings"""
    verify_auth(email, password)
    
    try:
        await db.settings.update_one(
            {"type": "google_sheets_sync"},
            {
                "$set": {
                    "type": "google_sheets_sync",
                    "google_sheets_url": google_sheets_url,
                    "auto_sync_enabled": auto_sync_enabled,
                    "sync_interval_minutes": sync_interval_minutes,
                    "updated_at": datetime.now(timezone.utc)
                }
            },
            upsert=True
        )
        return {"success": True, "message": "Settings saved"}
    except Exception as e:
        logger.error(f"Error saving sync settings: {e}")
        raise HTTPException(status_code=500, detail="Failed to save settings")


@api_router.post("/dashboard/sync-google-sheets")
async def sync_google_sheets(
    email: str = Query(...),
    password: str = Query(...),
    sheet_url: Optional[str] = Query(None)
):
    """
    Manually trigger Google Sheets sync.
    Fetches leads from Google Sheet and imports new ones.
    """
    verify_auth(email, password)
    
    try:
        # Get sheet URL from settings if not provided
        if not sheet_url:
            settings = await db.settings.find_one({"type": "google_sheets_sync"})
            if settings:
                sheet_url = settings.get("google_sheets_url")
        
        if not sheet_url:
            raise HTTPException(status_code=400, detail="No Google Sheets URL configured. Please add your Sheet URL in settings.")
        
        # Fetch CSV from Google Sheets
        logger.info(f"Syncing from Google Sheet: {sheet_url}")
        csv_text = await fetch_google_sheet_csv(sheet_url)
        
        # Parse CSV to leads
        leads = parse_csv_to_leads(csv_text)
        logger.info(f"Parsed {len(leads)} leads from sheet")
        
        if not leads:
            return ImportResult(
                success=True,
                imported=0,
                skipped=0,
                message="No leads found in the Google Sheet"
            )
        
        # Import leads (checking for duplicates)
        imported = 0
        skipped = 0
        
        for lead in leads:
            try:
                lead_email = lead.get("email", "")
                phone = lead.get("phone", "")
                
                # Skip empty rows
                if not lead.get("name") and not lead_email and not phone:
                    skipped += 1
                    continue
                
                # Check for duplicates (by email or phone in last 30 days)
                is_duplicate = await check_duplicate_lead(lead_email, phone, hours=720)
                if is_duplicate:
                    skipped += 1
                    continue
                
                # Parse date if provided
                created_at = datetime.now(timezone.utc)
                date_str = lead.get("date", "")
                if date_str:
                    for fmt in ["%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M:%S", "%d/%m/%Y", "%Y-%m-%d", "%m/%d/%Y"]:
                        try:
                            created_at = datetime.strptime(date_str.split(".")[0].strip(), fmt)
                            if created_at.tzinfo is None:
                                created_at = created_at.replace(tzinfo=timezone.utc)
                            break
                        except ValueError:
                            continue
                
                # Save lead
                lead_doc = {
                    "lead_id": str(uuid.uuid4()),
                    "name": lead.get("name", ""),
                    "email": lead_email,
                    "phone": str(phone),
                    "city": lead.get("city", ""),
                    "country": lead.get("country", ""),
                    "source": "google_sheets",
                    "status": "new",
                    "campaign": "Google Ads",
                    "platform": "google_sheets_sync",
                    "extra_data": {"synced_from": "google_sheets", "sync_time": datetime.now(timezone.utc).isoformat()},
                    "created_at": created_at,
                }
                
                await db.leads.insert_one(lead_doc)
                imported += 1
                
            except Exception as e:
                logger.error(f"Failed to import lead: {e}")
                skipped += 1
        
        # Update last sync time
        sync_result = f"Imported {imported}, skipped {skipped}"
        await db.settings.update_one(
            {"type": "google_sheets_sync"},
            {
                "$set": {
                    "last_sync": datetime.now(timezone.utc).isoformat(),
                    "last_sync_result": sync_result
                }
            },
            upsert=True
        )
        
        logger.info(f"Google Sheets sync complete: {sync_result}")
        
        return ImportResult(
            success=True,
            imported=imported,
            skipped=skipped,
            message=f"Sync complete! Imported {imported} new leads, skipped {skipped} (duplicates or empty)"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Google Sheets sync error: {e}")
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")


# ==================== DASHBOARD ENDPOINTS ====================

@api_router.post("/dashboard/login")
async def dashboard_login(request: LoginRequest):
    """Email + Password login for dashboard"""
    user_info = verify_credentials(request.email, request.password)
    if user_info["valid"]:
        token = generate_token(request.email)
        return {
            "success": True,
            "message": "Login successful",
            "token": token,
            "user": {
                "email": user_info["email"],
                "name": user_info["name"],
                "access": user_info["access"]
            }
        }
    raise HTTPException(status_code=401, detail="Invalid email or password")


@api_router.get("/dashboard/verify")
async def verify_login(email: str = Query(...), password: str = Query(...)):
    """Verify dashboard credentials"""
    user_info = verify_credentials(email, password)
    if user_info["valid"]:
        return {
            "valid": True,
            "email": user_info["email"],
            "user": {
                "email": user_info["email"],
                "name": user_info["name"],
                "access": user_info["access"]
            }
        }
    raise HTTPException(status_code=401, detail="Invalid credentials")


@api_router.get("/dashboard/stats")
async def get_dashboard_stats(email: str = Query(...), password: str = Query(...)):
    """Get dashboard statistics - filtered by user access"""
    user_info = verify_auth(email, password)
    source_filter = get_source_filter(user_info)
    
    try:
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Apply source filter to all queries
        total_leads = await db.leads.count_documents(source_filter)
        today_filter = {**source_filter, "created_at": {"$gte": today_start}}
        today_leads = await db.leads.count_documents(today_filter)
        
        # Source-specific counts (only if user has access to all or specific sources)
        if user_info["access"] == "all":
            website_leads = await db.leads.count_documents({"source": "website"})
            meta_leads = await db.leads.count_documents({"source": "meta"})
            google_leads = await db.leads.count_documents({"source": {"$in": ["google", "google_sheets"]}})
            university_change_leads = await db.leads.count_documents({"source": "university_change"})
            other_leads = await db.leads.count_documents({"source": {"$nin": ["website", "meta", "google", "google_sheets", "university_change"]}})
        elif user_info["access"] == "university_change":
            website_leads = 0
            meta_leads = 0
            google_leads = 0
            university_change_leads = total_leads
            other_leads = 0
        else:  # main_landing
            website_leads = await db.leads.count_documents({**source_filter, "source": "website"})
            meta_leads = await db.leads.count_documents({**source_filter, "source": "meta"})
            google_leads = await db.leads.count_documents({**source_filter, "source": {"$in": ["google", "google_sheets"]}})
            university_change_leads = 0
            other_leads = await db.leads.count_documents({**source_filter, "source": {"$nin": ["website", "meta", "google", "google_sheets"]}})
        
        return {
            "total_leads": total_leads,
            "today_leads": today_leads,
            "by_source": {
                "website": website_leads,
                "meta": meta_leads,
                "google": google_leads,
                "university_change": university_change_leads,
                "other": other_leads
            },
            "user_access": user_info["access"]
        }
        new_leads = await db.leads.count_documents({"status": "new"})
        contacted_leads = await db.leads.count_documents({"status": "contacted"})
        converted_leads = await db.leads.count_documents({"status": "converted"})
        
        return DashboardStats(
            total_leads=total_leads,
            today_leads=today_leads,
            website_leads=website_leads,
            meta_leads=meta_leads,
            google_leads=google_leads,
            other_leads=other_leads,
            new_leads=new_leads,
            contacted_leads=contacted_leads,
            converted_leads=converted_leads
        )
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch statistics")


@api_router.get("/dashboard/leads")
async def get_leads(
    email: str = Query(...),
    password: str = Query(...),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    source: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc")
):
    """Get paginated list of leads with filters - filtered by user access"""
    user_info = verify_auth(email, password)
    source_filter = get_source_filter(user_info)
    
    try:
        # Start with source filter based on user access
        query = {**source_filter}
        
        # Apply additional filters
        if source:
            if source == "google":
                query["source"] = {"$in": ["google", "google_sheets"]}
            else:
                query["source"] = source
        if status:
            query["status"] = status
        if search:
            query["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"email": {"$regex": search, "$options": "i"}},
                {"phone": {"$regex": search, "$options": "i"}},
                {"city": {"$regex": search, "$options": "i"}}
            ]
        
        total = await db.leads.count_documents(query)
        sort_dir = -1 if sort_order == "desc" else 1
        skip = (page - 1) * per_page
        
        cursor = db.leads.find(query).sort(sort_by, sort_dir).skip(skip).limit(per_page)
        leads_docs = await cursor.to_list(length=per_page)
        
        leads = []
        for doc in leads_docs:
            leads.append(LeadResponse(
                id=doc.get("lead_id", str(doc.get("_id", ""))),
                name=doc.get("name", ""),
                email=doc.get("email", ""),
                phone=doc.get("phone", ""),
                city=doc.get("city", ""),
                country=doc.get("country", ""),
                source=doc.get("source", "website"),
                status=doc.get("status", "new"),
                created_at=doc.get("created_at", datetime.now(timezone.utc)).isoformat() if isinstance(doc.get("created_at"), datetime) else str(doc.get("created_at", "")),
                campaign=doc.get("campaign"),
                platform=doc.get("platform"),
                extra_data=doc.get("extra_data")
            ))
        
        return LeadsListResponse(
            leads=leads,
            total=total,
            page=page,
            per_page=per_page
        )
    except Exception as e:
        logger.error(f"Error fetching leads: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch leads")


@api_router.patch("/dashboard/leads/{lead_id}/status")
async def update_lead_status(
    lead_id: str,
    status: str = Query(...),
    email: str = Query(...),
    password: str = Query(...)
):
    """Update lead status"""
    verify_auth(email, password)
    
    if status not in ["new", "contacted", "converted", "closed"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    try:
        result = await db.leads.update_one(
            {"lead_id": lead_id},
            {"$set": {"status": status, "updated_at": datetime.now(timezone.utc)}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        return {"success": True, "message": f"Status updated to {status}"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating lead status: {e}")
        raise HTTPException(status_code=500, detail="Failed to update status")


@api_router.delete("/dashboard/leads/{lead_id}")
async def delete_lead(
    lead_id: str,
    email: str = Query(...),
    password: str = Query(...)
):
    """Delete a lead"""
    verify_auth(email, password)
    
    try:
        result = await db.leads.delete_one({"lead_id": lead_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        return {"success": True, "message": "Lead deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting lead: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete lead")


@api_router.get("/dashboard/export")
async def export_leads(
    email: str = Query(...),
    password: str = Query(...),
    source: Optional[str] = Query(None),
    status: Optional[str] = Query(None)
):
    """Export leads as JSON"""
    verify_auth(email, password)
    
    try:
        query = {}
        if source:
            query["source"] = source
        if status:
            query["status"] = status
        
        cursor = db.leads.find(query, {"_id": 0}).sort("created_at", -1)
        leads = await cursor.to_list(length=10000)
        
        for lead in leads:
            if isinstance(lead.get("created_at"), datetime):
                lead["created_at"] = lead["created_at"].isoformat()
            if isinstance(lead.get("updated_at"), datetime):
                lead["updated_at"] = lead["updated_at"].isoformat()
        
        return {"leads": leads, "total": len(leads)}
    except Exception as e:
        logger.error(f"Error exporting leads: {e}")
        raise HTTPException(status_code=500, detail="Failed to export leads")


# ==================== SETUP INFO ENDPOINT ====================

@api_router.get("/setup-info")
async def get_setup_info():
    """Return webhook URLs and setup instructions"""
    base_url = os.environ.get("BASE_URL", "https://your-domain.com")
    
    return {
        "webhooks": {
            "universal": f"{base_url}/api/webhook/lead",
            "facebook": f"{base_url}/api/webhook/facebook",
            "google": f"{base_url}/api/webhook/google",
        },
        "facebook_setup": {
            "verify_token": FB_VERIFY_TOKEN,
            "webhook_url": f"{base_url}/api/webhook/facebook",
            "steps": [
                "1. Go to developers.facebook.com and create an app",
                "2. Add 'Webhooks' product to your app",
                "3. Subscribe to 'leadgen' field for your Page",
                f"4. Use verify token: {FB_VERIFY_TOKEN}",
                "5. Connect your Lead Ads form to your Page"
            ]
        },
        "google_sheets_import": {
            "endpoint": f"{base_url}/api/dashboard/import-sheets",
            "steps": [
                "1. Export your Google Sheet as JSON or CSV",
                "2. Use the import feature in dashboard",
                "3. Map columns: name, email, phone, city, country, source, date"
            ]
        }
    }


# ==================== APP SETUP ====================

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    await startup_db_client()


@app.on_event("shutdown")
async def shutdown_event():
    await shutdown_db_client()
