# VisaXpert Lead Integration Setup Guide

## Dashboard Access

**URL:** `https://your-domain.com/dashboard`

**Credentials:**
- Email: `admin@visaxpert.com`
- Password: `VisaXpert@2024`

---

## 1. Meta (Facebook/Instagram) Lead Ads Integration

### Step-by-Step Setup:

1. **Create Facebook App**
   - Go to [developers.facebook.com](https://developers.facebook.com)
   - Click "Create App" → Choose "Business" type
   - Fill in app name (e.g., "VisaXpert Leads")

2. **Add Webhooks Product**
   - In your app dashboard, click "Add Product"
   - Find "Webhooks" and click "Set Up"

3. **Configure Page Webhook**
   - In Webhooks section, select "Page" from dropdown
   - Click "Subscribe to this object"
   - Enter these details:
     ```
     Callback URL: https://your-domain.com/api/webhook/facebook
     Verify Token: visaxpert_leads_2024
     ```
   - Click "Verify and Save"

4. **Subscribe to leadgen**
   - After verification, find "leadgen" in the fields list
   - Click "Subscribe" next to it

5. **Connect to Your Facebook Page**
   - Go to your Facebook Page Settings
   - Navigate to "Leads" or "Lead Form"
   - Connect your app to receive leads

6. **Test the Integration**
   - Create a test lead form in Facebook Ads Manager
   - Submit a test lead
   - Check your dashboard - the lead should appear!

---

## 2. Google Ads Lead Form Integration

Google Ads doesn't support direct webhooks, so we use Google Sheets as an intermediary.

### Step-by-Step Setup:

1. **Enable Google Sheets in Google Ads**
   - Go to Google Ads → Tools & Settings → Lead Form Extensions
   - Click on your lead form extension
   - Under "Lead delivery options", enable "Google Sheets"
   - Create or select a Google Sheet

2. **Export Leads from Google Sheets**
   - Open the connected Google Sheet
   - Go to File → Download → CSV (.csv)

3. **Import to Dashboard**
   - Open VisaXpert Dashboard
   - Click "Import" button in header
   - Upload your CSV file or paste the data
   - Click "Import Leads"

### CSV Format Expected:
```csv
name,email,phone,city,country,date
John Doe,john@example.com,9876543210,Delhi,Canada,2024-01-15
Jane Smith,jane@example.com,9123456789,Mumbai,UK,2024-01-16
```

---

## 3. Universal Webhook (Custom Integrations)

For any custom system, send a POST request:

**Endpoint:** `POST https://your-domain.com/api/webhook/lead`

**Payload:**
```json
{
  "name": "Lead Name",
  "email": "lead@example.com",
  "phone": "9876543210",
  "city": "Delhi",
  "country": "Canada",
  "source": "custom",
  "campaign": "Campaign Name"
}
```

**Response:**
```json
{
  "success": true,
  "lead_id": "uuid-here",
  "message": "Lead received successfully"
}
```

---

## Webhook URLs Summary

| Platform | URL |
|----------|-----|
| Facebook/Meta | `https://your-domain.com/api/webhook/facebook` |
| Google (via import) | `https://your-domain.com/api/dashboard/import-sheets` |
| Universal | `https://your-domain.com/api/webhook/lead` |

---

## Environment Variables (for VPS deployment)

Add these to your `.env` file:

```env
DASHBOARD_EMAIL=admin@visaxpert.com
DASHBOARD_PASSWORD=VisaXpert@2024
FB_VERIFY_TOKEN=visaxpert_leads_2024
FB_APP_SECRET=your_facebook_app_secret_here
```

---

## Troubleshooting

### Facebook Webhook Not Verifying
- Check that your server is accessible from the internet
- Verify the token matches exactly: `visaxpert_leads_2024`
- Check server logs: `sudo journalctl -u visaxpert -f`

### Leads Not Appearing
- Check MongoDB connection
- Verify Google Sheets webhook is configured
- Test with curl: `curl -X POST your-domain.com/api/webhook/lead -H "Content-Type: application/json" -d '{"name":"Test"}'`

### Import Failing
- Ensure CSV has headers: name, email, phone, city, country
- Check for duplicate leads (same email/phone in last 30 days are skipped)
