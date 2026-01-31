"""
Test script for the scrape endpoint.
Usage: python test_scrape.py [url]

If no URL is provided, uses a default Wayfair test URL.
"""
import requests
import time
import sys
import json
from database import get_db

# Default test URL
DEFAULT_URL = "https://www.wayfair.ca/furniture/pdp/birch-lane-lorna-bookcase-c000432609.html?piid=988896039&auctionId=5cc3d3a7-b4e6-4e2c-8626-f904c99405f4&trackingId=%7B%22adType%22%3A%22WSP%22%2C%22auctionId%22%3A%225cc3d3a7-b4e6-4e2c-8626-f904c99405f4%22%7D&adTypeId=1"

BASE_URL = "http://127.0.0.1:8000"


def test_scrape(url: str):
    """Run a scrape test and return results."""
    print("=" * 60)
    print("SCRAPE TEST")
    print("=" * 60)
    print(f"URL: {url}\n")

    # 1. Call scrape endpoint
    print("1. Calling /scrape endpoint...")
    try:
        response = requests.post(f"{BASE_URL}/scrape", params={"url": url})
        response.raise_for_status()
        data = response.json()

        job_id = data.get("job_id")
        product_id = data.get("product_id")

        print(f"   Job ID: {job_id}")
        print(f"   Product ID: {product_id}")
        print(f"   Status: {data.get('status')}")
        print(f"   Message: {data.get('message')}\n")
    except requests.exceptions.ConnectionError:
        print("   ERROR: Could not connect to server. Is it running?")
        print("   Run: python -m uvicorn main:app --reload")
        return
    except Exception as e:
        print(f"   ERROR: {e}")
        return

    # 2. Poll for completion
    print("2. Polling for job completion...")
    max_attempts = 60  # 60 seconds max
    attempt = 0

    while attempt < max_attempts:
        try:
            progress_response = requests.get(f"{BASE_URL}/progress/{job_id}")
            progress = progress_response.json().get("progress")

            print(f"   [{attempt+1}s] Status: {progress}")

            if progress in ["completed", "failed"]:
                break

            time.sleep(1)
            attempt += 1
        except Exception as e:
            print(f"   ERROR polling: {e}")
            break

    print()

    # 3. Get database details directly
    print("3. Fetching database records...")
    db = get_db()

    # Get product
    product = db.get_product(product_id)

    # Get job
    job = db.get_job(job_id)

    # 4. Print results
    print("\n" + "=" * 60)
    print("PRODUCT RECORD")
    print("=" * 60)
    print(json.dumps(product, indent=2, default=str))

    print("\n" + "=" * 60)
    print("JOB RECORD")
    print("=" * 60)
    print(json.dumps(job, indent=2, default=str))

    # 5. Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    if product:
        print(f"  Title: {product.get('title', 'N/A')}")
        print(f"  Price: {product.get('price', 'N/A')}")
        print(f"  Status: {product.get('status', 'N/A')}")
        print(f"  Missing Fields: {product.get('missing_fields', [])}")

    if job:
        print(f"  Job Status: {job.get('status', 'N/A')}")
        if job.get('error'):
            print(f"  Job Error: {job.get('error')}")

    return product, job


if __name__ == "__main__":
    # Get URL from command line or use default
    url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_URL
    test_scrape(url)