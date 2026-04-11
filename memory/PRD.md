# VisaXpert Landing Page - PRD

## Original Problem Statement
Build a landing page for VisaXpert - a study abroad specialist since 2012 with 3500+ success stories. Landing page for Google/Meta Ads with quick enquiry form. Dashboard to view and manage all leads from multiple sources.

## User Personas
- **Primary**: Gen-Z Indian students (17-25 years) looking to study abroad
- **Secondary**: Parents of students seeking consultation
- **Admin**: VisaXpert staff managing leads

## Core Requirements
- Quick enquiry form with validation
- 4 branch locations: Ludhiana, Amritsar, Pathankot, Jammu
- Contact: 9875985641
- Ad-compliant copy, fast & responsive
- Dashboard to view and manage all leads
- Direct integration with Meta/Google Ads (no Zapier)

## What's Been Implemented

### Landing Page (December 2025)
- [x] Hero section with enquiry form
- [x] Form validation (10-digit Indian phone, email required)
- [x] Services section (6 services)
- [x] Stats section (3500+ success stories)
- [x] Destination cards (12 countries A-Z sorted)
- [x] Testimonials section
- [x] Branch locations (Ludhiana, Amritsar, Pathankot, Jammu)
- [x] WhatsApp floating button (9915503107)
- [x] Sticky scroll CTA bar
- [x] Privacy Policy modal with disclaimer
- [x] "Other" country option with text input
- [x] Thank You modal with branch addresses

### Landing Page UI Overhaul (March 2026)
- [x] Trust Badges under hero heading (3500+ Visas, 14+ Years Experience, IAF Accredited)
- [x] Partner Universities section with tabbed country selector and horizontal slider (logos only, no names)
- [x] Founder Video section with placeholder (YouTube/HTML5 video ready)
- [x] Removed "Visit Us at Our Offices" section (branch info retained in footer only)
- [x] Footer restructured: 4 columns (About, India Branches, International Presence, Contact)

### University Change Page Updates (March 2026)
- [x] Removed blue color scheme, replaced with white/emerald theme
- [x] Removed comparison section (public vs private)
- [x] Added German university logos section (TU Berlin, FU Berlin, Humboldt, HTW, Beuth, SRH, ESMT, Bard)
- [x] Form: Removed date/time, added "Mode of Consultation" dropdown (Berlin Office, Phone, Google Meet)
- [x] Updated services wording: "Private University to Public University" (full text)
- [x] Updated all FAQs with new detailed content
- [x] Enhanced VisaXpert branding throughout the page
- [x] Changed all blue accents to emerald green

### Tracking & Analytics
- [x] Google Tag Manager (GTM-N5CN3GKP)
- [x] Google Ads Conversion Tracking (AW-17858205001)
- [x] Custom dataLayer events (form_submit, call_click, whatsapp_click)

### Leads Dashboard (March 2026)
- [x] Email + Password authentication
- [x] Lead statistics (total, today, by source)
- [x] Leads table with search, filter, pagination
- [x] Lead status management (new, contacted, converted, closed)
- [x] CSV export functionality
- [x] Lead detail modal
- [x] Setup/Integration guide modal

### Direct Integrations (March 2026) - NO ZAPIER
- [x] **Facebook Webhooks**: Direct endpoint for Meta Lead Ads
  - Webhook verification endpoint (GET)
  - Lead receiver endpoint (POST)
  - Verify Token: `visaxpert_leads_2024`
- [x] **Google Sheets Auto-Sync**: Auto-import leads from Google Sheets
  - Configure sheet URL in dashboard
  - One-click sync button
  - Duplicate detection (30 days)
  - Supports any Google Sheet with Name, Email, Phone columns
- [x] **Manual CSV Import**: Upload CSV files directly
- [x] **Universal Webhook**: For any custom integration

## Tech Stack
- Frontend: React + Tailwind CSS + Shadcn UI
- Backend: FastAPI + MongoDB
- Database: MongoDB (leads collection)

## API Endpoints

### Public Endpoints
- `POST /api/enquiry` - Submit website enquiry form

### Webhook Endpoints
- `GET /api/webhook/facebook` - Facebook webhook verification
- `POST /api/webhook/facebook` - Receive Meta Lead Ads
- `POST /api/webhook/google` - Receive Google leads
- `POST /api/webhook/lead` - Universal webhook

### Dashboard Endpoints (email + password auth)
- `POST /api/dashboard/login` - Authenticate with email/password
- `GET /api/dashboard/verify` - Verify credentials
- `GET /api/dashboard/stats` - Get statistics
- `GET /api/dashboard/leads` - Get paginated leads
- `PATCH /api/dashboard/leads/{id}/status` - Update status
- `DELETE /api/dashboard/leads/{id}` - Delete lead
- `GET /api/dashboard/export` - Export leads
- `POST /api/dashboard/import-sheets` - Import from Google Sheets

## Credentials

### Dashboard Login
- Email: `admin@visaxpert.com`
- Password: `VisaXpert@2024`

### Facebook Webhook
- Verify Token: `visaxpert_leads_2024`

## Deployment

### Preview
- URL: https://destination-connect-2.preview.emergentagent.com
- Dashboard: https://destination-connect-2.preview.emergentagent.com/dashboard

### Live (Hostinger VPS)
- URL: visaxpertinternational.co.in
- Dashboard: visaxpertinternational.co.in/dashboard

## Setup Guides
- `/app/GOOGLE_SHEETS_SETUP.md` - Apps Script for form → sheets
- `/app/INTEGRATION_SETUP.md` - Meta & Google integration setup

## Dashboard Credentials

### User 1: Navya Arora
- **Email**: navyaarora@visaxpert.co
- **Password**: VisaXpert@2024
- **Access**: University Change leads only

### User 2: Sunil Arora
- **Email**: sunilarora@visaxpert.co
- **Password**: VisaXpert@2024
- **Access**: Main Landing Page leads only (website, meta, google - excludes university_change)

### Admin (Full Access)
- **Email**: admin@visaxpert.com
- **Password**: VisaXpert@2024
- **Access**: All leads

## Next Tasks
1. Upload actual university logos to `/app/frontend/public/assets/universities/` (placeholder paths already configured)
2. Add founder video (YouTube embed URL or upload MP4 to VPS)
3. Update founder name/title in video section
4. Deploy updated code to VPS
5. Create Facebook App and configure webhooks
6. Enable Google Sheets sync in Google Ads
7. Test end-to-end lead flow

## VPS Deployment Commands
After pulling latest code, run:
```bash
cd /var/www/visaxpert
git stash  # or git checkout . to discard changes
git pull origin main
cd frontend && npm run build
sudo systemctl restart visaxpert-backend
```

## Future Enhancements (Backlog)
- Email notifications for new leads
- SMS notifications via Twilio
- Lead scoring/prioritization
- Multi-user dashboard with roles
- Analytics charts and reports
- WhatsApp Business API integration
