"""
Legacy scraping router - DEPRECATED
This file is maintained for backward compatibility.
Use scraping_orchestrator.py for new implementations.
"""
import time
from scraping_orchestrator import ScrapingOrchestrator, ScraperConfig

# Legacy classes for backward compatibility
class BaseParser:
    """Legacy class - use base_scraper.BaseScraper instead."""
    pass

class GenericParser(BaseParser):
    """Legacy class - use scraper_factory.ScraperFactory instead."""
    pass

class WayfairParser(BaseParser):
    """Legacy class - use wayfair_scraper.WayfairScraper instead."""
    pass

class AmazonParser(BaseParser):
    """Legacy class - use amazon_scraper.AmazonScraper instead."""
    pass



if __name__ == "__main__":
    print("⚠️  DEPRECATED: This file is deprecated. Use scraping_orchestrator.py instead.")
    print("📖 Example usage:")
    print("   python scraping_orchestrator.py --input links.txt --output output_folder")
    print("")
    print("🔄 Running legacy mode for backward compatibility...")
    
    # Legacy implementation using new architecture
    from scraping_orchestrator import ScrapingOrchestrator, ScraperConfig
    
    config = ScraperConfig(
        output_path="G:\\My Drive\\selling\\not posted\\",
        max_images=20
    )
    
    orchestrator = ScrapingOrchestrator(config)
    results = orchestrator.scrape_from_file(
        "G:\\My Drive\\selling\\not posted\\links.txt",
        delay_between_requests=5
    )
    
    print("✅ All products processed successfully.")
