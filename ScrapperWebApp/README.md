# Furniture Scraper Web Application

A FastAPI-based web application that scrapes product data from e-commerce sites (Amazon, Wayfair, etc.) and stores it in Supabase for later posting to Facebook Marketplace.

## Overview

```
User pastes URL → API creates job → Scraper extracts data → Images upload to Supabase → Data saved to database
```

## Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: Supabase (PostgreSQL)
- **Storage**: Supabase Storage (for product images)
- **Scraping**: Selenium + undetected-chromedriver + BeautifulSoup

---

## Project Structure

```
ScrapperWebApp/
├── main.py                 # FastAPI app & endpoints
├── database.py             # Supabase database operations
├── jobs.py                 # Job management (create, get, update)
├── models.py               # Pydantic data models
├── config.py               # Environment variables & settings
├── scrapper_service.py     # High-level scraping interface
├── test_scrape.py          # Test script for debugging
├── requirements.txt        # Python dependencies
├── database_schema.sql     # SQL schema for Supabase
│
└── Scraping/               # Scraping module
    ├── __init__.py
    ├── base_scraper.py     # Abstract base class for scrapers
    ├── scraper_factory.py  # Factory to select correct scraper
    ├── amazon_scraper.py   # Amazon-specific scraper
    ├── wayfair_scraper.py  # Wayfair-specific scraper
    ├── generic_scraper.py  # Fallback for any e-commerce site
    └── models.py           # ProductData dataclass
```

---

## Key Files Explained

### `main.py`
The FastAPI application entry point. Contains:
- `POST /scrape` - Main endpoint to scrape a URL
- `GET /progress/{job_id}` - Check job status
- `GET /results_job/{job_id}` - Get job results
- `scrape_and_update()` - Background task that runs scraping

**Flow:**
1. Receives URL from user
2. Creates product record in database
3. Creates job linked to product
4. Queues background scraping task
5. Returns immediately with job_id

### `database.py`
Supabase client wrapper with all database operations:
- **Products**: create, get, update, list
- **Jobs**: create, get, update status
- **Images**: upload to storage, save references
- Uses singleton pattern (`get_db()`)

### `jobs.py`
Job management layer between API and database:
- `create_job(product_id, job_type)` - Creates new job
- `get_job(job_id)` - Retrieves job
- `get_progress(job_id)` - Returns job status

### `scrapper_service.py`
High-level scraping interface:
- `scrape_url(url)` - Takes URL, returns `ScrappedData` object
- Creates appropriate scraper via factory
- Handles configuration (output path, max images)

### `Scraping/base_scraper.py`
Abstract base class all scrapers inherit from:
- Chrome driver initialization with anti-detection
- Image downloading
- Directory creation for product files
- Common utility methods

### `Scraping/scraper_factory.py`
Factory pattern to select correct scraper:
```python
ScraperFactory.create_scraper(url)
# Returns: AmazonScraper, WayfairScraper, or GenericScraper
```

---

## Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. USER REQUEST                                             │
│    POST /scrape?url=https://amazon.com/product              │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. CREATE RECORDS                                           │
│    • Create product in DB (status: pending)                 │
│    • Create job linked to product (status: pending)         │
│    • Return job_id immediately                              │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. BACKGROUND SCRAPING (scrape_and_update)                  │
│    • Update job status → "running"                          │
│    • ScraperFactory selects correct scraper                 │
│    • Scraper opens Chrome, navigates to URL                 │
│    • Extracts: title, price, description, images            │
│    • Downloads images to temp folder                        │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. SAVE TO DATABASE                                         │
│    • Upload images to Supabase Storage                      │
│    • Update product with scraped data                       │
│    • Update job status → "completed"                        │
│    • Store image URLs in product_images table               │
└─────────────────────────────────────────────────────────────┘
```

---

## Database Schema

### `products`
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| url | TEXT | Source URL (unique) |
| title | TEXT | Product title |
| price | TEXT | Product price |
| description | TEXT | Product description |
| status | ENUM | pending, collected, ready_to_post, posted, sold, failed |
| missing_fields | TEXT[] | Fields that couldn't be scraped |

### `jobs`
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| product_id | UUID | Foreign key to products |
| job_type | ENUM | scrape, post |
| status | ENUM | pending, running, completed, failed |
| result | JSONB | Scraped data (title, price, images, etc.) |
| error | TEXT | Error message if failed |

### `product_images`
| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| product_id | UUID | Foreign key to products |
| file_path | TEXT | Supabase Storage public URL |
| image_order | INT | Display order |

---

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Create `.env` file:
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
```

### 3. Setup Supabase
1. Create a new Supabase project
2. Run `database_schema.sql` in SQL Editor
3. Create storage bucket named `product-images`
4. Add storage policies for INSERT and SELECT (see below)

### 4. Storage Policies
In Supabase → Storage → product-images → Policies:

**Allow uploads:**
- Operation: INSERT
- Target roles: anon, authenticated
- Policy: `bucket_id = 'product-images'`

**Allow reads:**
- Operation: SELECT
- Target roles: anon, authenticated
- Policy: `bucket_id = 'product-images'`

---

## Running

### Start the Server
```bash
python -m uvicorn main:app --reload
```

Server runs at: http://127.0.0.1:8000

### API Docs
Visit: http://127.0.0.1:8000/docs

### Test Scraping
```bash
python test_scrape.py
# Or with custom URL:
python test_scrape.py "https://amazon.com/dp/B08N5WRWNW"
```

---

## API Endpoints

### `POST /scrape`
Start scraping a URL.

**Request:**
```
POST /scrape?url=https://www.wayfair.ca/furniture/pdp/...
```

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "product_id": "abc123-def456",
  "status": "pending",
  "message": "Scraping started in background"
}
```

### `GET /progress/{job_id}`
Check job status.

**Response:**
```json
{
  "progress": "running"  // or "completed", "failed"
}
```

### `GET /results_job/{job_id}`
Get full job results.

**Response:**
```json
{
  "result": {
    "job_id": "...",
    "status": "completed",
    "result": {
      "title": "Product Name",
      "price": "$99.99",
      "description": "...",
      "images": ["https://supabase.co/.../image1.jpg", ...]
    }
  }
}
```

---

## Supported Sites

| Site | Scraper | Notes |
|------|---------|-------|
| Amazon (.com, .ca, .co.uk) | AmazonScraper | Full support |
| Wayfair (.com, .ca) | WayfairScraper | Anti-bot bypass included |
| Any other | GenericScraper | Uses meta tags, may have limited data |

---

## Product Status Flow

```
pending → collected → ready_to_post → posted → sold
              ↓
           failed (if error)
```

- **pending**: Just created, scraping not started
- **collected**: Scraped but missing some fields
- **ready_to_post**: All fields present, ready for Facebook
- **posted**: Posted to Facebook Marketplace
- **sold**: Item has been sold
- **failed**: Error during scraping

---

## Troubleshooting

### Chrome Version Mismatch
The app uses `webdriver-manager` to auto-download the correct ChromeDriver. If issues persist:
```bash
pip install --upgrade webdriver-manager
# Clear cache:
rmdir /s "C:\Users\{username}\.wdm"
```

### Supabase Storage 403 Error
Add storage policies (INSERT and SELECT) for the `product-images` bucket.

### Import Errors
Make sure you're running from the `ScrapperWebApp` directory:
```bash
cd ScrapperWebApp
python -m uvicorn main:app --reload
```

---

## Future Enhancements

- [ ] Web UI dashboard
- [ ] Facebook Marketplace posting integration
- [ ] Bulk URL import
- [ ] Manual field editing
- [ ] "Mark as Sold" functionality