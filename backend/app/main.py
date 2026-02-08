from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

from app.api.v1.router import api_router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Set all CORS enabled origins
origins = []
if settings.BACKEND_CORS_ORIGINS:
    origins.extend([str(origin) for origin in settings.BACKEND_CORS_ORIGINS])

# Explicitly add production and local frontend
origins.extend([
    "http://localhost:3000",
    "https://dental-frontend-963321342744.us-central1.run.app",
    "https://executivechiefos.com",
])

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"^https://.*\.lovable(project)?\.(app|com)$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok"}
