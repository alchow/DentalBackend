from mcp.server.fastmcp import FastMCP
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from uuid import UUID

# Import internal app components
from app.db.session import SessionLocal
from app.models import Patient, Visit, Note, Bill
from app.core.security import get_blind_index, decrypt_data, encrypt_data

# Initialize FastMCP Server
mcp = FastMCP("DentalNotesBackend")

async def get_db_session():
    async with SessionLocal() as session:
        yield session

@mcp.tool()
async def search_patients(last_name: str) -> list[dict]:
    """Search for patients by last name (exact match required for security)."""
    async with SessionLocal() as db:
        blind_index = get_blind_index(last_name)
        result = await db.execute(select(Patient).filter(Patient.last_name_hash == blind_index))
        patients = result.scalars().all()
        
        output = []
        for p in patients:
            output.append({
                "id": str(p.id),
                "first_name": decrypt_data(p.first_name),
                "last_name": decrypt_data(p.last_name),
                "dob": str(p.dob)
            })
        return output

@mcp.tool()
async def get_patient_history(patient_id: str) -> dict:
    """Get full history (visits, notes, bills) for a patient."""
    async with SessionLocal() as db:
        # Fetch Patient with relationships
        stmt = select(Patient).where(Patient.id == UUID(patient_id)).options(
            selectinload(Patient.visits),
            selectinload(Patient.notes),
            selectinload(Patient.bills)
        )
        result = await db.execute(stmt)
        patient = result.scalars().first()
        
        if not patient:
            return {"error": "Patient not found"}
            
        history = {
            "patient": {
                "id": str(patient.id),
                "first_name": decrypt_data(patient.first_name),
                "last_name": decrypt_data(patient.last_name),
            },
            "visits": [{"date": str(v.visit_date), "reason": v.reason} for v in patient.visits],
            "notes": [{"date": str(n.created_at), "content": decrypt_data(n.content)} for n in patient.notes],
            "bills": [{"amount": str(b.amount), "status": b.status} for b in patient.bills]
        }
        return history

@mcp.tool()
async def create_visit(patient_id: str, reason: str, visit_date: str) -> str:
    """Schedule a new visit."""
    from datetime import datetime
    async with SessionLocal() as db:
        dt = datetime.fromisoformat(visit_date)
        visit = Visit(
            patient_id=UUID(patient_id),
            visit_date=dt,
            reason=reason,
            status="SCHEDULED"
        )
        db.add(visit)
        await db.commit()
        return f"Visit created with ID: {visit.id}"

@mcp.tool()
async def add_clinical_note(patient_id: str, content: str, author_id: str, visit_id: str = None) -> str:
    """Add a sensitive clinical note. Encrypts content automatically."""
    async with SessionLocal() as db:
        note = Note(
            patient_id=UUID(patient_id),
            visit_id=UUID(visit_id) if visit_id else None,
            content=encrypt_data(content),
            author_id=author_id
        )
        db.add(note)
        await db.commit()
        return f"Note added with ID: {note.id}"
