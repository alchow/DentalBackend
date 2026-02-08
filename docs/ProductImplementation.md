Dental Practice Management - iPad Frontend Design
Target Device: iPad (1024×768 minimum, optimized for 1366×1024)
User: Solo dentist managing their own practice
Core Philosophy: Minimize taps, maximize clinical focus

Design Summary
This document outlines the complete frontend design for an iPad-focused dental practice management app. The design is based on two provided mockups and the backend API specification.

Key Design Principles
Principle	Implementation
Clinical Safety First	Allergies always visible in headers
Minimize Taps	Quick phrases, keyboard shortcuts, modal patterns
iPad Native Feel	3-panel layout, 44pt touch targets, gesture support
Focus Mode	Charting as modal overlay removes distractions
User Review Required
IMPORTANT

Decisions Needed Before Implementation

✅ Resolved
Visual Tooth Chart → Text-first for experienced dentists, optional chart for newbies (Phase 2)

Patient Browse Flow → Added dedicated Patients icon in rail + browse/sort/search flow

Task Search → Added search within Task view (filters by patient name and description)

⏳ Still Need Your Input
Grouped Quick Phrases: Do you want quick phrases organized by category (Findings, Treatment, Follow-up) with collapsible sections, or keep the flat list shown in the mockup?

Notifications Content: What should appear in the Notifications view?

 Appointment reminders (e.g., "Sarah Mitchell in 15 min")
 Overdue task alerts
 Patient follow-up reminders
 Other: _____________
Risk Badge Calculation: The MainNav shows "Moderate Risk" on the patient. How is this determined?

 Manually set by dentist
 Auto-calculated from allergies + medical conditions
 Not needed for MVP
Design Decisions & Recommendations
1. Three-Panel Master-Detail Layout (Recommended ✓)
Based on the screenshot, I'm using a three-panel layout optimized for iPad landscape:

┌─────────┬──────────────────┬────────────────────────────┐
│  Icon   │   Context List   │       Detail Panel         │
│  Rail   │   (Schedule/     │   (Patient Info, Notes,    │
│  (64px) │   Tasks/Alerts)  │    Charting, etc.)         │
│         │   (280px)        │   (remaining width)        │
└─────────┴──────────────────┴────────────────────────────┘
Rationale: This pattern is used by iPadOS Mail, Files, and most medical EHRs. It keeps context visible while allowing deep-dives.

2. User Flows
Flow 1: Morning Routine (Schedule View)
No
Yes
Open App
Logged In?
Login Screen
Schedule View - Today
See Appointments List
Tap Patient Name
Patient Detail Drawer
Review Items to Address
Review Last Visit Summary
Start Visit → Charting
Flow 2: Clinical Documentation (Charting)
Yes
No
Start Visit
Charting View Opens
Patient Header - Name/DOB/Allergies
Optional: Select Oral Area
Optional: Select Tooth #
Optional: Select Surface
Note Type Selector
Type Clinical Notes
Use Quick Keys
Save Note
More Notes?
Complete Visit
Flow 3: New Patient Registration (Dentist-Initiated)
Tap + New Patient
Patient Form Modal
Enter Name, DOB
Contact Info - Phone, Email
Medical History
Allergies - Multi-select
Current Medications
Insurance Info
Save Patient
Schedule First Visit?
Flow 4: Ad-hoc Patient Lookup (Search)
Tap Find Patient ⌘K
Search Modal Opens
Type Patient Name
Results Appear - Debounced
Tap Patient
Patient Detail View
Flow 5: Patient Browse (All Patients)
Tap Patients Icon in Rail
Patient List View
Scroll Through All Patients
Sort: A-Z / Recent / Next Appt
Type in Search Field
Tap Patient Row
Filtered Results
Patient Detail Panel
TIP

Design Note: Patient Browse uses the same 3-panel layout. Icon Rail shows a dedicated "Patients" icon (👥) separate from Schedule. This supports the common workflow of "I need to find someone who called but isn't on today's schedule."

Flow 6: Task Management
Tap Tasks Icon
Task List View
Filter: Due Today / This Week / All
Search: Type patient or description
Tap Task
Filtered Results
Task Detail Panel
Mark Complete
Open Related Patient
Dismiss Task
Edit Task
TIP

Design Note: Task search filters by patient name AND task description. Example: typing "crown" finds all tasks mentioning crowns across all patients.

Flow 7: Account Setup (First-Time)
Download/Open App
Welcome Screen
Create Account
Practice Name
Dentist Email/Password
Account Created
Import Patients? - Future
Main Dashboard
Screen Specifications
Screen 1: Login / Registration
Element	Specification
Layout	Centered card on gradient background
Logo	Practice logo or app branding
Tabs	"Sign In" / "Create Account"
Fields (Login)	Email, Password
Fields (Register)	Practice Name, Address, Full Name, Email, Password, Confirm
Actions	Submit button, "Forgot Password?" link
Screen 2: MainNav - Schedule View (Primary)
MainNav Screenshot
Review
MainNav Screenshot

Zone	Contents
Icon Rail (Left)	Schedule 📅, Patients 👥, Tasks ✓, Notifications 🔔, Settings ⚙️
List Panel	Date header with nav arrows, Time slots with appointments
Detail Panel Header	Back arrow, Patient name, DOB, "Find Patient ⌘K", "+ Add Note ⌘N"
Detail Panel Body	Items to Address Today (tasks), Last Visit Summary, Patient Card
Patient Card Components:

Avatar/Initials with Risk Badge (Low/Moderate/High)
Age • DOB • Insurance
Allergies (red warning chip)
Medications (blue chip)
Last Visit date
Communication preference
"See Patient Details" link
Screen 3: MainNav - Tasks View
Zone	Contents
List Panel	Task filters (Due Today / This Week / All Pending), Task cards with patient name, description, due date
Detail Panel	Selected task details, Related patient info, Action buttons (Complete, Dismiss, Open Patient)
Screen 4: MainNav - Notifications View
Zone	Contents
List Panel	Notification list grouped by date/time
Detail Panel	Notification details, Related entity actions
Suggested Notification Types:

Appointment reminders
Task due alerts
Patient follow-up reminders
Bills pending review
Screen 5: Charting View (Modal Overlay) — CRITICAL PATH
IMPORTANT

This is the most frequently used screen. Every design decision here directly impacts clinical efficiency.

Reference Screenshots
MainNav - Schedule View
Review
MainNav - Schedule View

Screenshot Analysis
Element	Current Design	Analysis
Header	"New Clinical Note for [Patient]" + Allergy badge	✅ Excellent — allergies always visible (patient safety)
Tooth/Area	Free-text input + quick-select pills	✅ Flexible — allows "#14", "lower right quadrant", or "full mouth"
Note Type	Chip selector (7 options)	✅ Good variety: Chief Complaint, Finding, Treatment, Patient Concern, Follow-up Note, Phone Call, Lab Communication
Clinical Note	Large textarea	✅ Good size, but could use more vertical space
Quick Phrases	"+[phrase]" buttons	✅ Tappable, but layout could be more organized
Actions	Cancel + Save Note (duplicated in header)	⚠️ Redundant — streamline to one save button
Design Recommendations (Head Designer)
1. ✅ Keep: Modal Overlay Pattern
The modal works well because:

Focus: Removes distractions from schedule/patient list
Context: Patient name + allergies in header keeps context
iPad Optimized: Modal centers content for comfortable reach
2. 🔧 Enhance: Quick Phrase Organization
Current State: Flat list of 11+ phrases, hard to scan

Recommendation: Group by clinical context with collapsible sections

┌─────────────────────────────────────────────────────────────────┐
│ Quick Phrases                                              [+]  │
├─────────────────────────────────────────────────────────────────┤
│ ▼ FINDINGS                                                      │
│   [+ No issues noted] [+ Sensitivity to cold] [+ Bleeding...]  │
│ ▼ TREATMENT                                                     │
│   [+ Discussed with patient] [+ Patient tolerated well]        │
│ ▼ FOLLOW-UP                                                     │
│   [+ Needs follow-up] [+ Will monitor] [+ Good home care]      │
│ ► CUSTOM (collapsed by default)                                 │
└─────────────────────────────────────────────────────────────────┘
3. ✅ Keep: Text-First Tooth/Area Input (Optimized for Experienced Dentists)
Current State: Text field + 7 area pills — This is correct for the target user.

Design Decision: Keep text-first input as the primary interface. Experienced dentists type faster than they can tap through visual selectors.

┌─────────────────────────────────────────────────────────────────┐
│ Tooth / Area (optional)                                         │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │ #14, 30 MO                                                  │ │
│ └─────────────────────────────────────────────────────────────┘ │
│                                                                 │
│ [Upper Right] [Upper Left] [Lower Right] [Lower Left]           │
│ [Full Mouth] [Upper Anterior] [Lower Anterior]                  │
│                                                                 │
│ [🦷 Tooth Chart] ← Optional helper for new users               │
└─────────────────────────────────────────────────────────────────┘
Future Enhancement (Phase 2): Visual tooth chart as an optional popover for:

New dentists learning the system
Complex multi-tooth documentation
Training mode for dental students
The chart would be accessible via the [🦷 Tooth Chart] button but NOT the default workflow:

Upper
   1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16
   ○  ○  ○  ○  ○  ○  ○  ○  ○  ○  ○  ○  ○  ●  ○  ○
   ─────────────────────────────────────────────
   ○  ○  ○  ○  ○  ○  ○  ○  ○  ○  ○  ○  ○  ○  ○  ○
  32 31 30 29 28 27 26 25 24 23 22 21 20 19 18 17
        Lower
Rationale: Optimize for the 80% case (experienced dentist typing quickly). Visual chart is nice-to-have, not must-have.

4. 🔧 Enhance: Note Type Visibility
Current State: "Finding" is selected (teal), others are gray pills

Recommendation: Add category icons and color coding

Note Type	Icon	Color	When Used
Chief Complaint	💬	Blue	Patient's stated reason
Finding	🔍	Teal	Clinical observations
Treatment	💉	Green	Procedures performed
Patient Concern	⚠️	Yellow	Non-clinical concerns
Follow-up Note	📋	Purple	Continuing care
Phone Call	📞	Gray	Documented calls
Lab Communication	🧪	Orange	Lab orders/results
5. 🔧 Enhance: Keyboard Optimization
Since dentists often use iPad with keyboard:

Shortcut	Action
⌘ + Enter	Save Note
Esc	Cancel/Close
Tab	Navigate fields
⌘ + 1-7	Select Note Type
/ in textarea	Open Quick Phrase picker
6. ⚠️ Remove: Duplicate Save Button
Current design has Save Note in header AND footer. Recommend:

Header: Keep only Close (×) button
Footer: [Cancel] [Save & New] [Save Note ✓]
"Save & New" allows rapid note entry for multi-finding visits.

Final Charting Modal Wireframe
┌─────────────────────────────────────────────────────────────────────┐
│ ×  New Clinical Note                                                │
│    for Sarah Mitchell   ⚠️ Penicillin, Latex                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ TOOTH / AREA (optional)                                             │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ #14                                                             │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│ [Upper Right] [Upper Left] [Lower Right] [Lower Left] [Full Mouth]  │
│ [Upper Anterior] [Lower Anterior] [🦷 Tooth Chart]                  │
│                                                                     │
│ NOTE TYPE                                                           │
│ [💬 Chief Complaint] [🔍 Finding ✓] [💉 Treatment] [⚠️ Concern]     │
│ [📋 Follow-up] [📞 Phone Call] [🧪 Lab Comm]                        │
│                                                                     │
│ CLINICAL NOTE                                                       │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ Patient reports sensitivity to cold on #14. Diagnosed with     │ │
│ │ caries. Discussed treatment options.                           │ │
│ │                                                                 │ │
│ │ Type "/" for quick phrases...                                  │ │
│ │                                                                 │ │
│ │                                                                 │ │
│ │                                                                 │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                     │
│ QUICK PHRASES                                                       │
│ ▼ FINDINGS                                                          │
│ [+ No issues noted] [+ Sensitivity to cold] [+ Bleeding on probing] │
│ ▼ TREATMENT                                                         │
│ [+ Patient tolerated well] [+ Discussed with patient]               │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│                     [Cancel]  [Save & New]  [✓ Save Note]           │
└─────────────────────────────────────────────────────────────────────┘
Implementation Notes
API Mapping (from 

frontend_api_spec.md
):

Create note: POST /api/v1/notes
Fields: patient_id, visit_id, content, tooth_number, surface_ids, note_type, area_of_oral_cavity
Note Type Values (match backend enum):

CHIEF_COMPLAINT, FINDING, TREATMENT, PATIENT_CONCERN, FOLLOW_UP, PHONE_CALL, LAB_COMMUNICATION
Quick Phrases:

Fetch: GET /api/v1/quick_phrases?category={category}
Create custom: POST /api/v1/quick_phrases
Track usage: PUT /api/v1/quick_phrases/{id} (increment usage_count)
Screen 6: Patient Detail (Modal or Panel)
Section	Fields
Header	Full name, Age, DOB, Avatar
Contact	Phone, Email, Address, Preferred contact method
Insurance	Provider, Policy #, Group #
Medical History	Conditions list
Allergies	List with severity
Medications	List with dosage
Visit History	List of past visits with summaries
Notes History	List of all clinical notes
Bills	Outstanding and historical
Screen 7: New/Edit Patient Form
Multi-section form with:

Demographics - Name, DOB, Gender
Contact - Phone, Email, Address
Emergency Contact - Name, Relationship, Phone
Insurance - Primary, Secondary
Medical History - Conditions, Surgeries
Allergies - Drug, Environmental, with severity
Medications - Current meds with dosage
Screen 8: New/Edit Visit Form
Field	Type
Patient	Searchable dropdown (required)
Date	Date picker (required)
Time	Time picker (required)
Duration	Dropdown: 15/30/45/60/90 min
Reason	Text field
Status	Dropdown: Scheduled, In Progress, Completed, Cancelled
Screen 9: Settings
Section	Options
Account	Name, Email, Password
Practice	Practice name, Address, Phone
Preferences	Default appointment duration, Tooth numbering system
Quick Phrases	CRUD for clinical shortcuts
API Keys	For integrations
Sign Out	
Component Library
Base Components
Component	Description
IconRail	Vertical navigation bar with icon buttons
ListPanel	Scrollable list with search/filter header
DetailPanel	Main content area with header and body
PatientCard	Summary card with key patient info
TaskCard	Task item with status, due date, patient link
ChipBadge	Colored badge for allergies, risk, status
Modal	Full-screen modal for forms
Dropdown	Touch-friendly select with large tap targets
QuickKeyGrid	Grid of shortcut buttons for charting
ToastNotification	Ephemeral feedback messages
iPad-Specific Patterns
Touch Targets: Minimum 44×44pt for all interactive elements
Gestures: Swipe-to-action on list items (mark complete, dismiss)
Keyboard: Floating iPad keyboard support, hardware keyboard shortcuts
Split View: Support iPadOS Split View (compact mode)
Hover States: Support for Magic Keyboard trackpad
Technical Architecture
Frontend Stack
Layer	Technology	Rationale
Framework	Next.js 14	SSR for fast initial load, App Router
Styling	CSS Modules + CSS Variables	Per your constraint to use vanilla CSS
State	React Context + SWR	Simple, handles caching well
Forms	React Hook Form	Performant form handling
Icons	Lucide React	Clean medical-appropriate icons
Date/Time	date-fns	Lightweight, locale-aware
Project Structure
frontend/
├── app/
│   ├── layout.tsx
│   ├── page.tsx (redirects to /schedule)
│   ├── (auth)/
│   │   ├── login/page.tsx
│   │   └── register/page.tsx
│   ├── (main)/
│   │   ├── layout.tsx (MainNav wrapper)
│   │   ├── schedule/page.tsx
│   │   ├── tasks/page.tsx
│   │   └── notifications/page.tsx
│   ├── charting/[visitId]/page.tsx
│   └── patients/
│       ├── page.tsx (list/search)
│       └── [patientId]/page.tsx (detail)
├── components/
│   ├── layout/
│   │   ├── IconRail.tsx
│   │   ├── ListPanel.tsx
│   │   └── DetailPanel.tsx
│   ├── patients/
│   │   ├── PatientCard.tsx
│   │   └── PatientForm.tsx
│   ├── charting/
│   │   ├── ChartingHeader.tsx
│   │   ├── ChartingForm.tsx
│   │   └── QuickKeyGrid.tsx
│   └── ui/
│       ├── Button.tsx
│       ├── Modal.tsx
│       └── ...
├── lib/
│   ├── api.ts (fetch wrapper with auth)
│   └── hooks/ (useSWR hooks)
├── styles/
│   ├── globals.css
│   ├── variables.css
│   └── components/
└── public/
Implementation Phases
Phase 1: Foundation (MVP)
 Project setup with Next.js
 Authentication (Login/Register)
 MainNav layout with Schedule view
 Patient list and detail view
 Basic charting form
Phase 2: Core Workflows
 Visit creation and scheduling
 Full charting with Quick Phrases
 Task management
 Patient CRUD
Phase 3: Polish
 Notifications system
 Search improvements
 Settings page
 Keyboard shortcuts
 iPad optimization testing
Verification Plan
Automated Tests
Component unit tests with React Testing Library
API integration tests with MSW
Accessibility audit with axe-core
Manual Verification
Test on iPad Pro 12.9" and 11"
Test with Smart Keyboard and Magic Keyboard
Test in portrait and landscape orientations
Test with VoiceOver for accessibility
Open Questions for Discussion
Billing Workflow: The API has Bills, but should we include detailed billing management, or just surface basic info? Full billing may need dedicated screens.

Visit Status Transitions: When should a visit move from SCHEDULED → IN_PROGRESS → COMPLETED? Auto on charting start/end, or manual?

Multi-dentist Future: You mentioned "solo dentist" but should the architecture support future multi-user practices?

Data Import: Any need to import existing patient data from another system in the initial release?