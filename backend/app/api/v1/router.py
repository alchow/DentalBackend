from fastapi import APIRouter
from app.api.v1.endpoints import patients, visits, notes, bills

api_router = APIRouter()
api_router.include_router(patients.router, prefix="/patients", tags=["patients"])
api_router.include_router(visits.router, prefix="/visits", tags=["visits"])
api_router.include_router(notes.router, prefix="/notes", tags=["notes"])
api_router.include_router(bills.router, prefix="/bills", tags=["bills"])
