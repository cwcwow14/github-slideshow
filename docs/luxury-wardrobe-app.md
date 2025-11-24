# Luxury Wardrobe & Stylist App – Build Guide

This guide outlines how to build the invitation-only luxury wardrobe sharing, stylist booking, and shopping guidance app discussed earlier. It favors a practical MVP-first approach with clear components, data models, and execution steps.

## Product pillars
1. **Profiles & onboarding**: style quiz, fit/measurement profile, invite-only access.
2. **Closet & sharing**: import items, authenticate, insure, list for rental with logistics concierge.
3. **Stylist marketplace**: book synchronous/async sessions, rates/tiers, delivery of look boards.
4. **Look building & shopping guidance**: AI + stylist generated looks, gap analysis, curated buys.
5. **Trust & payments**: ID verification, deposits/escrow, ratings, disputes, cleaning standards.

## Recommended stack
- **Mobile**: React Native (Expo) or SwiftUI for iOS-first; server-driven UI for dynamic look boards.
- **Backend**: Node.js (NestJS) or Rails API with GraphQL/REST; background jobs via BullMQ/Sidekiq.
- **Data**: PostgreSQL (relational core), Redis (sessions/queues), S3-compatible storage for media.
- **Infra**: Docker + Terraform; deploy on Fly.io/Render/Heroku for speed, migrate to AWS/GCP as you scale.
- **Payments & ID**: Stripe Connect (standard + custom accounts) for escrow/marketplace; Persona/Trulioo for KYC.
- **Search & feeds**: OpenSearch/Elasticsearch for filtering closets and stylists; feature-flagging via LaunchDarkly.
- **AI assists**: Vision tagging (brand/color/fabric), embedding-based outfit recommendations, and LLM prompts for look tips.

## Core service boundaries
- **Identity & access**: invitations, roles (member, stylist, admin), MFA, device management.
- **Closet**: item ingestion, metadata tagging, provenance docs, condition grading, availability calendar.
- **Sharing & logistics**: pricing, deposits, insurance, booking flow, shipping/returns, cleaning tasks.
- **Stylist marketplace**: profiles, tiers, calendar, booking, messaging/video, deliverables (look boards, notes).
- **Commerce**: escrow, payouts, dispute workflows, refunds, taxes/fees breakdown.
- **Content & recommendations**: look generation, seasonal capsules, closet gap analysis, shopping lists.

## Suggested schema (high level)
- `users`: identity, role, verification state, membership tier.
- `profiles`: measurements, style archetypes, preferences, tailor notes.
- `items`: brand, category, materials, colors, season, condition, authentication docs, owner.
- `listings`: price/day, deposit, insurance tier, availability, logistics preferences.
- `bookings`: start/end dates, status, shipping labels, cleaning tasks, disputes.
- `stylists`: bio, tier, rates, specialties, response SLA, calendar.
- `stylist_sessions`: mode (async/Live), deliverables, attachments, chat thread.
- `looks`: items (owned + recommended), notes, occasions, weather context, AI vs stylist source.
- `payments`: intents, holds, releases, fees, refunds, disputes; link to bookings and sessions.
- `ratings`: for lenders/borrowers/stylists; includes NPS + punctuality/condition sub-scores.

## MVP build steps (sequenced)
1. **Foundations**: auth (email/OTP + invite codes), profiles, measurements, image uploads, basic item tagging.
2. **Closet & sharing**: create/list items, availability calendar, pricing/deposits, rental booking flow, Stripe Connect integration, simple shipping labels (Shippo/EasyPost).
3. **Stylist booking**: stylist profiles + tiers, availability slots, booking + payment, async chat, file attachments for look boards.
4. **Look boards & guidance**: manual look creation with AI-assist for suggestions, closet gap analysis, wishlist with price alerts.
5. **Trust & ops**: KYC, ratings, dispute templates, cleaning/inspection tasks, audit logs.
6. **Launch gates**: invitation controls, feature flags, analytics (PostHog), error monitoring (Sentry), observability (OpenTelemetry + hosted backend).

## AI features (practical implementation)
- **Tagging**: use a hosted vision API (e.g., AWS Rekognition + custom labels) to detect brand cues/colors/fabrics; store embeddings to power similarity search for outfit pairing.
- **Outfit suggestions**: build a rules-first engine (season/occasion/weather) with LLM re-ranking. Log prompts/completions for safety and tuning.
- **Stylist assist**: prompt templating for look commentary and shopping notes; human editors approve for early cohorts.

## Operational workflows
- **Logistics**: generate prepaid labels, enforce return windows, auto-charge late fees, and trigger cleaning orders on return.
- **Disputes**: triage flow with evidence upload, hold funds until resolution, configurable policies per item tier.
- **Safety**: enforce PII and payments logging; RBAC for support/admin dashboards.

## Security & compliance
- Role-based access, per-tenant audit logs, secure media URLs, and rate limiting.
- PCI handled by Stripe; maintain webhooks for payment events. Consider GDPR/CCPA data rights flows.

## Go-to-market milestones
- **Private beta (4–6 weeks)**: invite 50–100 members; focus on closet import + stylist sessions + manual logistics.
- **Cohort scaling (6–10 weeks)**: automate shipping/cleaning, add ratings/disputes, expand stylists, refine AI tagging.
- **Growth (10+ weeks)**: introduce membership tiers, capsules, and dynamic recommendations; formalize affiliate/brand partnerships.

## Team & delivery
- **Week 1–2**: setup repo/CI/CD, auth, profiles, media uploads.
- **Week 3–4**: listings + bookings + payments; initial stylist flow.
- **Week 5–6**: look boards, AI tagging MVP, trust/safety basics.
- **Week 7–8**: polish UX, add analytics/observability, harden operations.

## Measuring success
- Conversion from invite to completed profile; time to first item listed.
- Stylist booking completion rate and NPS; repeat booking %.
- Rental completion without dispute; on-time return rate.
- Closet-to-look coverage and add-to-wishlist rate.

Use this as a blueprint to scope tasks, sequence your backlog, and align engineering with ops and styling teams.
