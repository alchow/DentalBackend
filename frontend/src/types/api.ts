/**
 * API Response Types
 * Mirroring backend Pydantic schemas from:
 * - backend/app/schemas/patient.py
 * - backend/app/schemas/visit_note.py
 * - backend/app/schemas/task.py
 * - backend/app/schemas/quick_phrase.py
 * - backend/app/schemas/bill.py
 * - backend/app/schemas/auth.py
 */

// =============================================================================
// Auth Types
// =============================================================================

export interface TokenResponse {
    access_token: string;
    token_type: 'bearer';
}

export interface UserLogin {
    email: string;
    password: string;
}

export interface OfficeCreate {
    name: string;
    address?: string;
}

export interface UserCreate {
    email: string;
    password: string;
    full_name: string;
}

export interface RegisterRequest {
    office: OfficeCreate;
    user: UserCreate;
}

export interface ApiKeyCreate {
    name: string;
}

export interface ApiKeyResponse {
    id: string;
    prefix: string;
    name: string;
    key?: string; // Only returned once on creation
    is_active: boolean;
    created_at: string;
}

// =============================================================================
// Patient Types
// =============================================================================

export interface ContactInfo {
    phone?: string;
    email?: string;
    address?: string;
}

export interface MedicalHistory {
    allergies?: string[];
    medications?: string[];
    conditions?: string[];
    [key: string]: unknown; // Allow additional unstructured data
}

export interface PatientBase {
    first_name: string;
    last_name: string;
    dob: string; // ISO date string (YYYY-MM-DD)
    contact_info?: ContactInfo;
    medical_history?: MedicalHistory;
}

export interface PatientCreate extends PatientBase { }

export interface PatientUpdate {
    first_name?: string;
    last_name?: string;
    dob?: string;
    contact_info?: ContactInfo;
    medical_history?: MedicalHistory;
}

export interface PatientResponse extends PatientBase {
    id: string;
    last_name_hash: string;
    created_at: string;
    updated_at: string;
}

// =============================================================================
// Visit Types
// =============================================================================

export type VisitStatus =
    | 'SCHEDULED'
    | 'IN_PROGRESS'
    | 'COMPLETED'
    | 'CANCELLED'
    | 'DELETED';

export interface VisitSummary {
    chief_complaint?: string;
    notes_count?: number;
    [key: string]: unknown;
}

export interface VisitBase {
    visit_date: string; // ISO datetime string
    reason?: string;
    status: VisitStatus;
    summary?: VisitSummary;
    patient_id: string;
}

export interface VisitCreate extends VisitBase { }

export interface VisitUpdate {
    visit_date?: string;
    reason?: string;
    status?: VisitStatus;
    summary?: VisitSummary;
}

export interface VisitResponse extends VisitBase {
    id: string;
    created_at: string;
    updated_at: string;
}

// =============================================================================
// Note Types
// =============================================================================

export type NoteType =
    | 'CHIEF_COMPLAINT'
    | 'FINDING'
    | 'TREATMENT'
    | 'PATIENT_CONCERN'
    | 'FOLLOW_UP'
    | 'PHONE_CALL'
    | 'LAB_COMMUNICATION'
    | 'GENERAL';

export interface NoteBase {
    content: string;
    area_of_oral_cavity?: string;
    tooth_number?: string;
    surface_ids?: string;
    note_type: NoteType | string;
    author_id: string;
    patient_id: string;
    visit_id?: string;
}

export interface NoteCreate extends NoteBase { }

export interface NoteUpdate {
    content: string;
    area_of_oral_cavity?: string;
    tooth_number?: string;
    surface_ids?: string;
    note_type?: NoteType | string;
    author_id: string;
}

export interface NoteResponse extends NoteBase {
    id: string;
    created_at: string;
    updated_at: string;
}

// =============================================================================
// Task Types
// =============================================================================

export type TaskStatus = 'PENDING' | 'COMPLETED' | 'DISMISSED';
export type TaskPriority = 'LOW' | 'NORMAL' | 'HIGH';

export interface TaskBase {
    description: string;
    status: TaskStatus;
    priority: TaskPriority;
    due_date?: string; // ISO date string
    patient_id: string;
    generated_by?: string;
}

export interface TaskCreate extends TaskBase { }

export interface TaskUpdate {
    description?: string;
    status?: TaskStatus;
    priority?: TaskPriority;
    due_date?: string;
}

export interface TaskResponse extends TaskBase {
    id: string;
    created_at: string;
    updated_at: string;
}

// =============================================================================
// Quick Phrase Types
// =============================================================================

export type QuickPhraseCategory = 'FINDING' | 'TREATMENT' | 'FOLLOW_UP' | 'CUSTOM';

export interface QuickPhraseBase {
    text: string;
    category?: QuickPhraseCategory | string;
}

export interface QuickPhraseCreate extends QuickPhraseBase { }

export interface QuickPhraseUpdate {
    text?: string;
    category?: string;
    usage_count?: number;
}

export interface QuickPhraseResponse extends QuickPhraseBase {
    id: string;
    usage_count: number;
}

// =============================================================================
// Bill Types
// =============================================================================

export type BillStatus = 'PENDING' | 'PAID' | 'PARTIALLY_PAID' | 'CANCELLED';

export interface CdtCode {
    id?: string;
    code: string;
    description?: string;
    category?: string;
}

export interface BillCreate {
    patient_id: string;
    visit_id?: string;
    amount: number;
    status: BillStatus;
    codes: string[]; // CDT code strings
}

export interface BillResponse {
    id: string;
    patient_id: string;
    visit_id?: string;
    amount: number;
    status: BillStatus;
    codes: CdtCode[];
    created_at: string;
    updated_at: string;
}

// =============================================================================
// Search Types
// =============================================================================

export interface SearchQuery {
    query: string;
    limit?: number;
}

// =============================================================================
// API Error Type
// =============================================================================

export interface ApiErrorDetail {
    detail: string;
    [key: string]: unknown;
}

// =============================================================================
// Pagination Types
// =============================================================================

export interface PaginationParams {
    limit?: number;
    offset?: number;
}

// =============================================================================
// Schedule Types (Frontend-specific)
// =============================================================================

export interface ScheduleEntry extends VisitResponse {
    patient?: PatientResponse;
}
