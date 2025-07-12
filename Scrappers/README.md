# Web Scraper - Improved Architecture

## Overview

This is a refactored web scraping system with improved architecture using modern software design patterns.

## Architecture Improvements

### 1. **Separation of Concerns**
- `base_scraper.py` - Abstract base class with common functionality
- `amazon_scraper.py` - Amazon-specific implementation
- `wayfair_scraper.py` - Wayfair-specific implementation
- `scraper_factory.py` - Factory pattern for creating scrapers
- `scraping_orchestrator.py` - Main orchestrator for batch processing

### 2. **Design Patterns Used**
- **Abstract Base Class**: Common interface for all scrapers
- **Factory Pattern**: Automatic scraper selection based on URL
- **Configuration Object**: Centralized configuration management
- **Result Object**: Structured return values

### 3. **Key Benefits**
- **Extensible**: Easy to add new site scrapers
- **Maintainable**: Clear separation of responsibilities
- **Configurable**: Centralized settings management
- **Robust**: Better error handling and recovery
- **Testable**: Modular design enables unit testing

## Usage

### New Architecture (Recommended)

```python
from scraping_orchestrator import ScrapingOrchestrator, ScraperConfig

# Configure scraper
config = ScraperConfig(
    output_path="./output/",
    max_images=20,
    request_delay=(2, 5)
)

# Create orchestrator
orchestrator = ScrapingOrchestrator(config)

# Scrape from file
results = orchestrator.scrape_from_file("links.txt")

# Or scrape individual URLs
urls = ["https://amazon.com/...", "https://wayfair.com/..."]
results = orchestrator.scrape_urls(urls)
```

### Command Line Interface

```bash
python scraping_orchestrator.py --input links.txt --output ./output --delay 5
```

### Legacy Support

The old `scraping_router.py` still works but uses the new architecture under the hood.

## Configuration Options

```python
ScraperConfig(
    output_path="./output/",     # Where to save products
    max_images=20,               # Max images per product
    request_delay=(2, 7),        # Random delay between requests
    timeout=10                   # Selenium timeout
)
```

## Adding New Scrapers

1. Create new scraper class inheriting from `BaseScraper`
2. Implement required abstract methods
3. Add to `ScraperFactory.SCRAPERS` list

Example:

```python
class NewSiteScraper(BaseScraper):
    SUPPORTED_DOMAINS = ['newsite.com']
    
    def is_supported_url(self, url: str) -> bool:
        return 'newsite.com' in url.lower()
    
    def extract_product_data(self) -> Optional[ProductData]:
        # Implementation here
        pass
    
    def extract_images(self) -> List[str]:
        # Implementation here
        pass
```

## Error Handling

The new architecture provides structured error handling:

```python
for result in results:
    if result.success:
        print(f"✅ {result.product.title}")
        print(f"📸 Downloaded {len(result.images)} images")
    else:
        print(f"❌ Error: {result.error}")
```
