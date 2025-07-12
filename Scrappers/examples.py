"""
Example usage of the improved scraping architecture.
"""
import os
import sys

# Add parent directory to path to import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraping_orchestrator import ScrapingOrchestrator, ScraperConfig


def example_single_url():
    """Example: Scrape a single URL."""
    print("=== Single URL Example ===")
    
    config = ScraperConfig(
        output_path="./output/",
        max_images=10
    )
    
    orchestrator = ScrapingOrchestrator(config)
    
    # Example URLs (replace with actual URLs)
    urls = [
        "https://www.amazon.com/example-product",
        "https://www.wayfair.com/example-product"
    ]
    
    results = orchestrator.scrape_urls(urls)
    
    for result in results:
        if result.success:
            print(f"✅ Successfully scraped: {result.product.title}")
        else:
            print(f"❌ Failed: {result.error}")


def example_from_file():
    """Example: Scrape URLs from a file."""
    print("=== File Input Example ===")
    
    # Create example links file
    example_links = [
        "https://www.amazon.com/example1",
        "https://www.wayfair.com/example2"
    ]
    
    with open("example_links.txt", "w") as f:
        f.write("\n".join(example_links))
    
    config = ScraperConfig(
        output_path="./output/",
        max_images=20
    )
    
    orchestrator = ScrapingOrchestrator(config)
    results = orchestrator.scrape_from_file("example_links.txt")
    
    print(f"Processed {len(results)} URLs")


def example_factory_usage():
    """Example: Direct factory usage."""
    print("=== Factory Pattern Example ===")
    
    from scraper_factory import ScraperFactory
    
    urls = [
        "https://www.amazon.com/example",
        "https://www.wayfair.com/example",
        "https://unsupported-site.com/example"
    ]
    
    for url in urls:
        scraper = ScraperFactory.create_scraper(url)
        if scraper:
            print(f"✅ Created {scraper.__class__.__name__} for {url}")
        else:
            print(f"❌ No scraper available for {url}")


if __name__ == "__main__":
    print("🚀 Web Scraper Examples")
    print("=" * 50)
    
    # Show supported domains
    from scraper_factory import ScraperFactory
    print(f"Supported domains: {ScraperFactory.get_supported_domains()}")
    print()
    
    # Run examples
    example_factory_usage()
    print()
    
    # Note: Actual scraping examples commented out to avoid running against real sites
    # Uncomment and provide real URLs to test
    
    # example_single_url()
    # example_from_file()
    
    print("✅ Examples completed")
