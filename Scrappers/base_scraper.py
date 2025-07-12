"""
Base scraper interface and abstract base class for web scraping.
"""
from abc import ABC, abstractmethod
import os
import re
import time
import requests
import undetected_chromedriver as uc
from typing import Optional, List, Dict, Any
from fake_useragent import UserAgent
from selenium.webdriver.chrome.options import Options
from models import ProductData
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class ScraperConfig:
    """Configuration class for scraper settings."""
    
    def __init__(self, 
                 output_path: str = "G:\\My Drive\\selling\\not posted\\",
                 max_images: int = 20,
                 request_delay: tuple = (2, 7),
                 timeout: int = 10):
        self.output_path = output_path
        self.max_images = max_images
        self.request_delay = request_delay
        self.timeout = timeout


class ScrapingResult:
    """Container for scraping results."""
    
    def __init__(self, success: bool = False, product: Optional[ProductData] = None, 
                 images: List[str] = None, error: Optional[str] = None):
        self.success = success
        self.product = product
        self.images = images or []
        self.error = error


class BaseScraper(ABC):
    """Abstract base class for web scrapers."""
    
    def __init__(self, url: str, config: Optional[ScraperConfig] = None):
        self.url = url
        self.config = config or ScraperConfig()
        self.driver = None
        self.images = []
        
    def _create_driver(self) -> uc.Chrome:
        """Create and configure Chrome driver."""
        opts = uc.ChromeOptions()
        opts.add_argument("--disable-gpu")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--disable-blink-features=AutomationControlled")
        opts.add_argument("--disable-infobars")
        
        ua = UserAgent()
        opts.add_argument(f'--user-agent={ua.random}')
        
        return uc.Chrome(options=opts)
    
    def _sanitize_filename(self, filename: str) -> str:
        """Remove invalid characters from filename."""
        return re.sub(r'[<>:\"/\\|?*]', '', filename)
    
    def _create_product_directory(self, product: ProductData) -> str:
        """Create directory structure for product."""
        sanitized_title = self._sanitize_filename(product.title)
        product_path = os.path.join(self.config.output_path, sanitized_title)
        
        if os.path.isdir(product_path):
            raise FileExistsError(f"Product directory already exists: {product_path}")
            
        os.makedirs(product_path, exist_ok=True)
        
        # Create photos subdirectory
        photos_dir = os.path.join(product_path, "Photos")
        os.makedirs(photos_dir, exist_ok=True)
        
        return product_path
    
    def _save_product_info(self, product: ProductData, product_path: str) -> None:
        """Save product information to text file."""
        info_file = os.path.join(product_path, "info.txt")
        
        with open(info_file, "w", encoding="utf-8") as f:
            f.write(f"Title: {product.title}\n")
            f.write(f"Price: {product.price}\n")
            f.write(f"Description: {product.description.strip()}\n")
            f.write(f"Link: {product.link}\n")
            if product.brand:
                f.write(f"Brand: {product.brand}\n")
            if product.color:
                f.write(f"Color: {product.color}\n")
            if product.tags:
                f.write(f"Tags: {product.tags}\n")
    
    def _download_images(self, product_path: str) -> List[str]:
        """Download images to product directory."""
        photos_dir = os.path.join(product_path, "Photos")
        downloaded_files = []
        
        for index, image_url in enumerate(self.images[:self.config.max_images]):
            try:
                response = requests.get(image_url, timeout=30)
                if response.status_code == 200:
                    filename = f'image_{index+1}.jpg'
                    filepath = os.path.join(photos_dir, filename)
                    
                    with open(filepath, 'wb') as file:
                        file.write(response.content)
                    
                    downloaded_files.append(filepath)
                    print(f"✅ Saved: {filepath}")
                else:
                    print(f"❌ Failed to download {image_url}: HTTP {response.status_code}")
                    
            except Exception as e:
                print(f'❌ Failed to download {image_url}: {e}')
                
        return downloaded_files
    
    @abstractmethod
    def extract_product_data(self) -> Optional[ProductData]:
        """Extract product data from the webpage."""
        pass
    
    @abstractmethod
    def extract_images(self) -> List[str]:
        """Extract image URLs from the webpage."""
        pass
    
    @abstractmethod
    def is_supported_url(self, url: str) -> bool:
        """Check if this scraper supports the given URL."""
        pass
    
    def scrape(self) -> ScrapingResult:
        """Main scraping method that orchestrates the entire process."""
        try:
            # Initialize driver
            self.driver = self._create_driver()
            
            # Extract product data
            product = self.extract_product_data()
            if not product:
                return ScrapingResult(success=False, error="Failed to extract product data")
            
            # Extract images
            self.images = self.extract_images()
            
            # Create directory and save data
            product_path = self._create_product_directory(product)
            self._save_product_info(product, product_path)
            downloaded_files = self._download_images(product_path)
            
            print(f"✅ Successfully scraped product: {product.title}")
            print(f"✅ Downloaded {len(downloaded_files)} images")
            
            return ScrapingResult(
                success=True, 
                product=product, 
                images=downloaded_files
            )
            
        except Exception as e:
            error_msg = f"Scraping failed for {self.url}: {str(e)}"
            print(f"❌ {error_msg}")
            return ScrapingResult(success=False, error=error_msg)
            
        finally:
            if self.driver:
                self.driver.quit()
