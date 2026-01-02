import uuid

# Jobs Hashmap
jobs = {}

def create_job(url: str):
    job_id = str(uuid.uuid4()) 
    jobs[job_id] = {
        "url": url,
        "status": "pending",
        "progress": {
            "page_loaded": False,
            "title_found": False,
            "price_found": False,
            "description_found": False
        },
        "result": None
    }
    return job_id

def get_progress(job_id: str):
    job = jobs.get(job_id)
    if not job:
        return None
    return{
        "status": job["status"],
        "progress": job["progress"]
    }

def get_results_job_id(job_id: str):
    job = jobs.get(job_id)
    if not job:
        return None
    return{
        "result": job["result"]
    }

def get_results():
    results = []
    for job_id, job in jobs.items():
        results.append({
            "job_id": job_id,
            "result": job["result"]
        })
    return results