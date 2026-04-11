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

### Landing Page Updates (April 2026)
- [x] Form headline: "Unlock Your Complimentary Profile Assessment"
- [x] Country dropdown: Canada, Germany, UK, Rest of Europe, Others
- [x] Destination cards: 4 countries (Canada, Germany, UK, Rest of Europe)
- [x] Logo scrolling speed 3x faster (8s animation)
- [x] CEO section: "Mr. Sunil Arora" / "CEO, VisaXpert"
- [x] Dynamic reviews/testimonials fetched from API

### Reviews Management System (April 2026)
- [x] Dashboard Reviews tab with full CRUD
- [x] Add Review modal: name, country, image URL, content, rating, page selector
- [x] Reviews appear dynamically on landing pages
- [x] Toggle review visibility (active/inactive)
- [x] Delete reviews
- [x] Page assignment: Main, University Change, Germany Fair
- [x] Star rating system (1-5)
- [x] Image URL support for student photos

### Germany Education Fair 2026 Landing Page (April 2026)
- [x] Route: /germany-fair
- [x] Hero section with registration form
- [x] Event schedule: Jammu (20th May), Pathankot (21st May), Amritsar (22nd May), Ludhiana (23rd May)
- [x] 8 participating universities with logos + auto-scrolling marquee
- [x] Benefits: €1000 discount, 50% fee waiver, meet reps, spot admissions
- [x] Beautiful event cards for each city
- [x] Leads go to dashboard with source "germany_fair"
- [x] WhatsApp integration
- [x] Thank you modal on registration
- [x] Responsive design

### Previous Landing Page (December 2025 - March 2026)
- [x] Hero section with enquiry form
- [x] Form validation (10-digit Indian phone, email required)
- [x] Services section (6 services)
- [x] Stats section (4000+ success stories)
- [x] Trust Badges (4000+ Visas, 14+ Years, ICEF Certified)
- [x] Partner Universities auto-scrolling marquee
- [x] CEO Video section placeholder
- [x] Branch locations footer
- [x] WhatsApp floating button
- [x] Sticky scroll CTA bar
- [x] Privacy Policy modal

### University Change Page
- [x] White/emerald theme
- [x] German university logos auto-scrolling
- [x] Form with Mode of Consultation dropdown
- [x] Welcome emails via Resend

### Tracking & Analytics
- [x] Google Tag Manager (GTM-N5CN3GKP)
- [x] Google Ads Conversion Tracking (AW-17858205001)
- [x] Custom dataLayer events

### Leads Dashboard
- [x] Multi-user authentication (role-based)
- [x] Lead statistics with source breakdown
- [x] Leads table with search, filter, pagination
- [x] Source filters: Website, Meta, Google, University Change, Germany Fair, IVR Calls
- [x] Lead status management (new, contacted, converted, closed)
- [x] CSV export
- [x] Google Sheets sync
- [x] Reviews management tab
- [x] Setup/Integration guide

### Direct Integrations - NO ZAPIER
- [x] Facebook Webhooks
- [x] Google Sheets Auto-Sync
- [x] Manual CSV Import
- [x] Universal Webhook
- [x] IVR/Missed Call Webhook
- [x] WhatsApp Business API
- [x] Resend Email

## Tech Stack
- Frontend: React + Tailwind CSS + Shadcn UI
- Backend: FastAPI + MongoDB
- Database: MongoDB (leads + reviews collections)

## API Endpoints

### Reviews Endpoints
- `GET /api/reviews?page=main` - Get active reviews (public)
- `POST /api/dashboard/reviews` - Create review (auth required)
- `GET /api/dashboard/reviews` - List all reviews (auth required)
- `DELETE /api/dashboard/reviews/{id}` - Delete review (auth required)
- `PATCH /api/dashboard/reviews/{id}/toggle` - Toggle active (auth required)

## Dashboard Credentials
### Admin (Full Access)
- Email: admin@visaxpert.com
- Password: VisaXpert@2024

### Sunil Arora (Main Landing)
- Email: sunilarora@visaxpert.co
- Password: VisaXpert@2024

### Navya Arora (University Change)
- Email: navyaarora@visaxpert.co
- Password: VisaXpert@2024

## Routes
- `/` - Main Landing Page
- `/dashboard` - Leads & Reviews Dashboard
- `/university-change` - University Change Page
- `/germany-fair` - Germany Education Fair 2026

## Next Tasks
1. Upload actual student photos for reviews
2. Add CEO video (YouTube embed)
3. Deploy to VPS
4. Share Germany Fair page link for ads

## Future Enhancements (Backlog)
- Email notifications for new leads
- SMS notifications via Twilio
- Lead scoring/prioritization
- Analytics charts and reports
- WhatsApp Business API improvements
- Review image upload (instead of URL)
