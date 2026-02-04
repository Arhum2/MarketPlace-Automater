from fastapi import FastAPI, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from jobs import create_job, get_progress, get_results_job_id, get_results
from models import CreateProductRequest, UpdateProductRequest
from scrapper_service import scrape_url
from database import get_db
from facebook_poster import post_to_facebook

app = FastAPI()

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


@app.post("/api/scrape")
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

@app.get("/api/progress/{job_id}")
async def check_progress(job_id: str):
    job_progress = get_progress(job_id)
    return {"progress": job_progress}

@app.get("/api/results_job/{job_id}")
async def check_result(job_id: str):
    job_result = get_results_job_id(job_id)
    return {"result": job_result}

@app.get("/api/results_jobs")
async def check_results():
    job_results = get_results()
    return {"results": job_results}


@app.get("/api/products")
async def list_products():
    """Get all products."""
    db = get_db()
    products = db.list_products()

    # Add first image thumbnail to each product
    for product in products:
        images = db.get_product_images(product['id'])
        product['thumbnail'] = images[0]['file_path'] if images else None

    return products


@app.get("/api/products/{product_id}")
async def get_product(product_id: str):
    """Get a single product by ID."""
    db = get_db()
    product = db.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.patch("/api/products/{product_id}")
async def update_product(product_id: str, request: UpdateProductRequest):
    """Update a product's fields."""
    db = get_db()
    product = db.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Build update data from non-None fields
    update_data = {k: v for k, v in request.model_dump().items() if v is not None}

    if not update_data:
        return product  # Nothing to update

    # Apply the update first
    updated = db.update_product(product_id, **update_data)

    # Check if all required fields are now complete
    images = db.get_product_images(product_id)
    missing_fields = []
    if not updated.get('title'):
        missing_fields.append('title')
    if not updated.get('price'):
        missing_fields.append('price')
    if not updated.get('description'):
        missing_fields.append('description')
    if not images:
        missing_fields.append('images')

    # Auto-update status based on completeness
    new_status = "ready_to_post" if not missing_fields else "collected"
    if updated.get('status') != new_status:
        updated = db.update_product(product_id, status=new_status, missing_fields=missing_fields)

    return updated


@app.delete("/api/products/{product_id}")
async def delete_product(product_id: str):
    """Delete a product by ID."""
    db = get_db()
    product = db.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete_product(product_id)
    return {"message": "Product deleted successfully"}


@app.get("/api/products/{product_id}/images")
async def get_product_images(product_id: str):
    """Get all images for a product."""
    db = get_db()
    images = db.get_product_images(product_id)
    return images


@app.delete("/api/products/{product_id}/images/{image_id}")
async def delete_product_image(product_id: str, image_id: str):
    """Delete a specific image from a product."""
    db = get_db()
    db.delete_product_image(image_id)
    return {"message": "Image deleted successfully"}


@app.post("/api/products/{product_id}/post")
async def post_product_to_facebook(product_id: str):
    """Post a product to Facebook Marketplace."""
    db = get_db()
    product = db.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Check if product has required fields
    if not product.get('title') or not product.get('price'):
        raise HTTPException(status_code=400, detail="Product missing title or price")

    # Check if product has images
    images = db.get_product_images(product_id)
    if not images:
        raise HTTPException(status_code=400, detail="Product has no images")

    # Post to Facebook (this will open browser and run automation)
    result = post_to_facebook(product_id)

    if result.get('success'):
        return {"message": result.get('message', 'Posted successfully')}
    else:
        raise HTTPException(status_code=500, detail=result.get('error', 'Posting failed'))


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