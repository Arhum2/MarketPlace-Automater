from fastapi import FastAPI
from ScrapperWebApp.jobs import create_job, jobs, get_progress, get_results_job_id, get_results

app = FastAPI()

@app.post("/scrape")
async def root(url: str):
    # Create job
    job_id = create_job(url)
    # TODO Start scrapper in background
    # Return immediately
    return {"job_id": job_id,
            "job": jobs[job_id]}

@app.get("/progress/{job_id}")
async def check_progress(job_id: str):
    job_progress = get_progress(job_id)
    return {"progress": job_progress}

@app.get("/results_job/{job_id}")
async def check_result(job_id: str):
    job_result = get_results_job_id(job_id)
    return {"result": job_result}

@app.get("/results_jobs")
async def check_results():
    job_results = get_results()
    return {"results": job_results}