from Scraping.base_scraper import ScraperConfig
from Scraping.scraper_factory import ScraperFactory
from models import ScrappedData
from config import TEMP_FOLDER, MAX_IMAGES


def scrape_url(url: str) -> ScrappedData:
    """Scrape a url and return scrapped data (models.py)"""

    try:
        config = ScraperConfig(
            output_path=TEMP_FOLDER,
            max_images=MAX_IMAGES
        )


        #Create a scraper
        scraper = ScraperFactory.create_scraper(url, config)

        if not scraper:
            raise Exception(f"No Scrapper Available for URL: {url}")
        
        #Scrape
        result = scraper.scrape()

        if not result.success:
            raise Exception(f"Scrapping failed: {result.error}")

        #Create ScrappedData object
        scrapped = ScrappedData(
            title=result.product.title if result.product else None,
            price=result.product.price if result.product else None,
            description=result.product.description if result.product else None,
            images=result.images or [],
            link=url
        )

        return scrapped
    
    except Exception as e:
        raise Exception(f"Scrapping error: {str(e)}")