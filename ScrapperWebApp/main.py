from fastapi import FastAPI, HTTPException, status, BackgroundTasks
from fastapi.responses import JSONResponse
from jobs import create_job, get_progress, get_results_job_id, get_results
from models import CreateProductRequest
from scrapper_service import scrape_url
from database import get_db

app = FastAPI()


def scrape_and_update(job_id: str, product_id: str, url: str):
    """Background task to scrape URL and update job/product."""
    db = get_db()

    try:
        # Update job status to "running"
        db.update_job_status(job_id, "running")

        # Scrape the URL
        scraped_data = scrape_url(url)

        # Check for missing fields
        missing_fields = []
        if not scraped_data.title:
            missing_fields.append("title")
        if not scraped_data.price:
            missing_fields.append("price")
        if not scraped_data.description:
            missing_fields.append("description")
        if not scraped_data.images or scraped_data.images == []:
            missing_fields.append("images")

        # Update product with scraped data
        db.update_product(
            product_id=product_id,
            title=scraped_data.title,
            price=scraped_data.price,
            description=scraped_data.description,
            status="ready_to_post" if not missing_fields else "collected",
            missing_fields=missing_fields
        )

        # Upload images to Supabase Storage
        image_urls = []
        if scraped_data.images:
            print(f"Uploading {len(scraped_data.images)} images to Supabase...")
            image_urls = db.upload_product_images(product_id, scraped_data.images)
            print(f"Uploaded {len(image_urls)} images successfully")

        # Update job with results
        db.update_job(
            job_id=job_id,
            status="completed",
            result={
                "title": scraped_data.title,
                "price": scraped_data.price,
                "description": scraped_data.description,
                "images": image_urls,  # Use Supabase URLs instead of local paths
                "link": scraped_data.link
            }
        )

    except Exception as e:
        # Update job as failed
        db.update_job_status(job_id, "failed", error=str(e))

        # Update product status
        db.update_product(product_id=product_id, status="failed")


@app.post("/scrape")
async def root(url: str, background_tasks: BackgroundTasks):
    db = get_db()

    # 1. Create product first
    product = db.create_product(url=url, status="pending")

    # 2. Create job linked to product
    job_id = create_job(product_id=product["id"], job_type="scrape")

    # 3. Queue scraping in background (non-blocking)
    background_tasks.add_task(scrape_and_update, job_id, product["id"], url)

    # 4. Return immediately
    return {
        "job_id": job_id,
        "product_id": product["id"],
        "status": "pending",
        "message": "Scraping started in background"
    }

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


@app.post("/api/products")
async def create_product(request: CreateProductRequest):
    db = get_db()
    existing_product = db.get_product_by_url(request.url)
    if existing_product:
        # Return existing product with 200 OK
        return JSONResponse(content=existing_product, status_code=status.HTTP_200_OK)
    
    # Create product
    try:
        product_data = db.create_product(request.url)
        return JSONResponse(content=product_data, status_code=status.HTTP_201_CREATED)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create product: {str(e)}")