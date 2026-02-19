# Page Design — Local Health Monitoring Web App (Desktop-first)

## Global Styles (All Pages)
- Layout system: Flexbox for header/toolbars; CSS Grid for main content columns and card layouts.
- Max content width: 1100–1200px centered; page padding 24px; card gap 16px.
- Typography:
  - Base: 16px, line-height 1.5
  - Headings: H1 28px, H2 20px, H3 16px
- Color tokens:
  - Background: #F7F8FA
  - Surface/Card: #FFFFFF
  - Text: #111827; Muted: #6B7280
  - Primary: #2563EB (buttons/links)
  - Success: #16A34A; Warning: #D97706; Danger: #DC2626
  - Border: #E5E7EB
- Buttons:
  - Primary: solid primary, white text; hover darken 6–8%; disabled 50% opacity
  - Secondary: white surface + border; hover background #F3F4F6
- Inputs:
  - 40px height, 8px radius, clear labels, helper text for ranges
- Responsiveness (desktop-first):
  - ≥1024px: 2-column dashboards (main + side)
  - 768–1023px: collapse to single column; charts stack
  - <768px: full-width controls, larger tap targets, sticky submit CTA on forms

## Shared Components
- Top Nav (all pages): App name (left), links (Dashboard, Daily Check-in, Medical Profile), “Export” shortcut.
- Page Header: Title + short description; optional “Last updated” meta.
- Card: title row + body; consistent padding 16–20px.
- Inline Status Badge: Low/Medium/High priority.

---

## Page 1: Dashboard
### Meta Information
- Title: “Dashboard | Local Health Monitor”
- Description: “Daily summary, recommendations, and simple health trends stored locally.”
- Open Graph: title + description; type=website (optional for local)

### Page Structure
- Header row: H1 “Dashboard” + “Start Daily Check-in” primary button.
- 2-column grid:
  - Left (main): Today Overview, Trends Snapshot, History Feed
  - Right (side): Recommendations card stack

### Sections & Components
1. Today Overview (Card)
   - Key-value rows: Sleep, Mood, Stress, Pain, Activity, Symptoms count
   - “Last check-in” timestamp
   - Empty state: prompt to complete first check-in
2. Recommendations (Card list)
   - Each item: Title, 1–2 line recommendation text, priority badge, “Why?” expand/collapse for rationale
   - Optional small score meter (0–1) as a thin progress bar
3. Trends Snapshot (Card)
   - Simple visuals: small inline SVG charts or table-based trends (7/30 days toggle)
   - Controls: date range dropdown; metric selector (sleep/mood/stress/pain/activity)
4. History Feed (Card)
   - Table: Date, quick highlights, “View” action
   - “View” opens an in-page modal/drawer (read-only entry details)

Interaction states
- Loading: skeleton rows for cards
- Errors: inline banner on fetch failure (local server unavailable)

---

## Page 2: Medical Profile
### Meta Information
- Title: “Medical Profile | Local Health Monitor”
- Description: “Your baseline and medical history used to contextualize recommendations.”

### Page Structure
- Single-column form layout with section cards; right-aligned Save button.

### Sections & Components
1. Baselines (Card)
   - Number inputs: Age, Height (cm), Weight (kg), Resting HR, Typical Sleep Hours
   - Helper text: accepted ranges and that fields are optional if unknown
2. Medical History (Card)
   - Multi-entry controls (chip input or textarea with one-per-line): Conditions, Surgeries, Family History
3. Medications & Allergies (Card)
   - Allergies: chip list
   - Medications: repeating rows (Name, Dose, Frequency) with Add/Remove
4. Notes (Card)
   - Free-text textarea
5. Data Management (Card)
   - Export: secondary button triggers file download (JSON)
   - Import: file picker + confirmation modal (warn overwrite)
6. Save Bar
   - Primary “Save Profile” button; success toast “Saved locally”

Validation
- Show field-level errors only when saving; keep forms forgiving.

---

## Page 3: Daily Check-in
### Meta Information
- Title: “Daily Check-in | Local Health Monitor”
- Description: “Log today’s wellness signals and get immediate recommendations.”

### Page Structure
- Two-column layout on desktop:
  - Left: form sections
  - Right: live preview of computed summary placeholders + after-submit results

### Sections & Components
1. Date + Quick Inputs (Card)
   - Date picker default today
   - Sleep hours (number) + sleep quality (1–5)
   - Mood (1–5) + stress (1–5)
2. Body & Symptoms (Card)
   - Pain slider (0–10)
   - Symptoms checklist (common items) + optional “Other” text
3. Activity & Notes (Card)
   - Activity minutes
   - Notes textarea
4. Submit (Sticky footer on smaller screens)
   - Primary “Save & Get Recommendations”
   - Secondary “Save Only” (optional if you want to skip model run)
5. Post-submit Summary (Right column / modal)
   - Show computed scores
   - Show recommendation list (same component as Dashboard)
   - CTA: “Back to Dashboard”

Accessibility
- Labels tied to inputs; keyboard-friendly sliders; sufficient contrast for badges and buttons.
