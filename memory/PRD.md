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
- [x] Destination cards (4 countries: Canada, Germany, UK, Rest of Europe)
- [x] Testimonials section
- [x] Branch locations (Ludhiana, Amritsar, Pathankot, Jammu)
- [x] WhatsApp floating button
- [x] Sticky scroll CTA bar
- [x] Privacy Policy modal with disclaimer
- [x] Thank You modal with branch addresses

### Landing Page Updates (April 2026)
- [x] Form headline changed to "Unlock Your Complimentary Profile Assessment"
- [x] Country dropdown reduced to 5 options: Canada, Germany, UK, Rest of Europe, Others
- [x] Destination cards reduced from 12 to 4 (Canada, Germany, UK, Rest of Europe)
- [x] Logo scrolling speed increased 3x (from 25s to 8s) on both landing pages
- [x] Founder video section updated: "CEO VisaXpert (Mr. Sunil Arora)"
- [x] Section heading changed from "Founder" to "CEO"

### Landing Page UI Overhaul (March 2026)
- [x] Trust Badges under hero heading (4000+ Visas, 14+ Years Experience, ICEF Certified)
- [x] Partner Universities section with auto-scrolling marquee
- [x] Founder Video section (now CEO section with Mr. Sunil Arora)
- [x] Footer restructured: 4 columns

### University Change Page
- [x] White/emerald theme
- [x] German university logos section (auto-scrolling)
- [x] Form with "Mode of Consultation" dropdown
- [x] Enhanced VisaXpert branding

### Tracking & Analytics
- [x] Google Tag Manager (GTM-N5CN3GKP)
- [x] Google Ads Conversion Tracking (AW-17858205001)
- [x] Custom dataLayer events

### Leads Dashboard (March 2026)
- [x] Email + Password authentication (multi-user)
- [x] Lead statistics (total, today, by source)
- [x] Leads table with search, filter, pagination
- [x] Lead status management
- [x] CSV export functionality
- [x] Google Sheets sync

### Direct Integrations - NO ZAPIER
- [x] Facebook Webhooks
- [x] Google Sheets Auto-Sync
- [x] Manual CSV Import
- [x] Universal Webhook
- [x] IVR/Missed Call Webhook
- [x] WhatsApp Business API
- [x] Resend Email (university change welcome emails)

## Tech Stack
- Frontend: React + Tailwind CSS + Shadcn UI
- Backend: FastAPI + MongoDB
- Database: MongoDB (leads collection)

## Dashboard Credentials
### User 1: Navya Arora
- Email: navyaarora@visaxpert.co
- Password: VisaXpert@2024
- Access: University Change leads only

### User 2: Sunil Arora
- Email: sunilarora@visaxpert.co
- Password: VisaXpert@2024
- Access: Main Landing Page leads only

### Admin (Full Access)
- Email: admin@visaxpert.com
- Password: VisaXpert@2024
- Access: All leads

## Next Tasks
1. Upload actual university logos
2. Add CEO video (YouTube embed URL)
3. Deploy updated code to VPS
4. Test end-to-end lead flow

## Future Enhancements (Backlog)
- Email notifications for new leads
- SMS notifications via Twilio
- Lead scoring/prioritization
- Analytics charts and reports
- WhatsApp Business API integration improvements
