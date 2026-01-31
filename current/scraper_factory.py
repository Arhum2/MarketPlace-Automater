"""
Scraper factory for creating appropriate scrapers based on URL.
"""
from typing import Optional, List
from urllib.parse import urlparse

from base_scraper import BaseScraper, ScraperConfig
from amazon_scraper import AmazonScraper
from wayfair_scraper import WayfairScraper
from generic_scraper import GenericScraper


class ScraperFactory:
    """Factory class for creating appropriate scrapers."""
    
    # Registry of available scrapers (order matters - specific scrapers first)
    SCRAPERS = [
        AmazonScraper,
        WayfairScraper,
        GenericScraper,  # Fallback for any URL
    ]
    
    @classmethod
    def create_scraper(cls, url: str, config: Optional[ScraperConfig] = None) -> Optional[BaseScraper]:
        """Create appropriate scraper for the given URL."""
        for scraper_class in cls.SCRAPERS:
            # Create temporary instance to check URL support
            temp_scraper = scraper_class(url, config)
            if temp_scraper.is_supported_url(url):
                return temp_scraper
        
        return None
    
    @classmethod
    def get_supported_domains(cls) -> List[str]:
        """Get list of all supported domains."""
        domains = []
        for scraper_class in cls.SCRAPERS:
            if hasattr(scraper_class, 'SUPPORTED_DOMAINS'):
                domains.extend(scraper_class.SUPPORTED_DOMAINS)
        return domains
    
    @classmethod
    def is_supported_url(cls, url: str) -> bool:
        """Check if any scraper supports the given URL."""
        return any(
            scraper_class(url).is_supported_url(url) 
            for scraper_class in cls.SCRAPERS
        )
