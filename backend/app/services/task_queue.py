"""Cloud Tasks integration for async job processing."""
import os
import json
import hashlib
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

logger = logging.getLogger(__name__)

# Redis for debounce tracking (optional, falls back to in-memory)
_debounce_cache: dict = {}


def get_debounce_key(patient_id: UUID) -> str:
    """Generate cache key for debounce tracking."""
    return f"summary_debounce:{patient_id}"


def should_debounce(patient_id: UUID) -> bool:
    """Check if summary generation should be debounced for this patient."""
    debounce_seconds = int(os.getenv("SUMMARY_DEBOUNCE_SECONDS", "300"))
    key = get_debounce_key(patient_id)
    
    now = datetime.now(timezone.utc)
    last_run = _debounce_cache.get(key)
    
    if last_run and (now - last_run).total_seconds() < debounce_seconds:
        return True
    
    return False


def mark_debounce(patient_id: UUID) -> None:
    """Mark that summary generation was triggered for this patient."""
    key = get_debounce_key(patient_id)
    _debounce_cache[key] = datetime.now(timezone.utc)


async def enqueue_summary_generation(
    patient_id: UUID, 
    note_id: UUID,
    office_id: UUID
) -> bool:
    """Enqueue a summary generation task via Cloud Tasks.
    
    Falls back to synchronous local generation if SUMMARY_SYNC_MODE=true
    and Cloud Tasks is not configured.
    
    Returns True if task was enqueued/generated, False if debounced or skipped.
    """
    if should_debounce(patient_id):
        logger.debug(f"Summary debounced for patient {patient_id}")
        return False
    
    mark_debounce(patient_id)
    
    # Check if Cloud Tasks is configured
    queue_name = os.getenv("CLOUD_TASKS_QUEUE")
    if not queue_name:
        # Cloud Tasks not configured - check for sync mode fallback
        sync_mode = os.getenv("SUMMARY_SYNC_MODE", "false").lower() == "true"
        if sync_mode:
            logger.info(f"Generating summary synchronously for patient {patient_id}")
            try:
                from app.services.summary_service import SummaryService
                from app.db.session import get_db_session
                
                async with get_db_session() as db:
                    service = SummaryService(db)
                    result = await service.generate_patient_summary(
                        patient_id=patient_id,
                        triggered_by_note_id=note_id,
                        office_id=office_id
                    )
                    if result:
                        logger.info(f"Summary generated successfully: {result.id}")
                    else:
                        logger.warning(f"Summary skipped for patient {patient_id} (no recent notes)")
                return True
            except Exception as e:
                logger.error(f"Sync summary generation failed for patient {patient_id}: {e}")
                return False
        else:
            logger.warning(
                "CLOUD_TASKS_QUEUE not configured and SUMMARY_SYNC_MODE not enabled. "
                "Set SUMMARY_SYNC_MODE=true for local development."
            )
            return False
    
    # Cloud Tasks async mode
    try:
        from google.cloud import tasks_v2
        
        project = os.getenv("GCP_PROJECT", "dentaldb-482716")
        location = os.getenv("CLOUD_TASKS_LOCATION", "us-central1")
        service_url = os.getenv("SERVICE_URL", "https://dental-backend-963321342744.us-central1.run.app")
        
        client = tasks_v2.CloudTasksClient()
        parent = client.queue_path(project, location, queue_name)
        
        payload = {
            "patient_id": str(patient_id),
            "note_id": str(note_id),
            "office_id": str(office_id)
        }
        
        task = {
            "http_request": {
                "http_method": tasks_v2.HttpMethod.POST,
                "url": f"{service_url}/api/v1/internal/generate-summary",
                "headers": {
                    "Content-Type": "application/json",
                    "X-Internal-Key": os.getenv("INTERNAL_API_KEY", ""),
                },
                "body": json.dumps(payload).encode(),
                "oidc_token": {
                    "service_account_email": os.getenv("SERVICE_ACCOUNT_EMAIL", "")
                }
            }
        }
        
        client.create_task(request={"parent": parent, "task": task})
        logger.info(f"Summary task enqueued for patient {patient_id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to enqueue summary task for patient {patient_id}: {e}")
        return False
