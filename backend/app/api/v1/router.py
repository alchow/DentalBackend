from fastapi import APIRouter
from app.api.v1.endpoints import patients, visits, notes, bills, tasks, quick_phrases, search

api_router = APIRouter()
api_router.include_router(patients.router, prefix="/patients", tags=["patients"])
api_router.include_router(visits.router, prefix="/visits", tags=["visits"])
api_router.include_router(notes.router, prefix="/notes", tags=["notes"])
api_router.include_router(bills.router, prefix="/bills", tags=["bills"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(quick_phrases.router, prefix="/quick_phrases", tags=["quick_phrases"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
