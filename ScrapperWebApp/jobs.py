from typing import List, Optional
from database import get_db


def create_job(product_id, job_type: str):
    """Create a new job and return its id"""
    db = get_db()

    job = db.create_job(
        product_id=product_id,
        job_type=job_type,
        status="pending"
    )

    return job["id"]

def get_job(job_id: str):
    """Return the job object if not found"""
    db = get_db()
    return db.get_job(job_id)

def get_progress(job_id: str):
    db = get_db()
    job = db.get_job(job_id)
    if not job:
        return None

    return job["status"]

def get_results_job_id(job_id: str) -> Optional[dict]:
    """Get formatted job result."""
    db = get_db()
    job = db.get_job(job_id)
    if not job:
        return None
    
    return {
        "job_id": job["id"],
        "product_id": job["product_id"],
        "job_type": job["job_type"],
        "status": job["status"],
        "result": job.get("result"),
        "error": job.get("error"),
        "created_at": job["created_at"]
    }

def get_results() -> List[dict]:
    """Get all jobs (you'll need to add this to database.py)."""
    db = get_db()
    # For now, return empty list - we'll add this later
    return []
