"""
Base scraper interface and abstract base class for web scraping.
"""
from abc import ABC, abstractmethod
import os
import re
import time
import requests
import undetected_chromedriver as uc
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Optional, List, Dict, Any
from fake_useragent import UserAgent
from selenium.webdriver.chrome.options import Options

# Import models from parent directory
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
from models import ProductData

# Load proxy list for rotation
def _load_proxies():
    """Load valid proxies from valid_proxies.txt"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    proxy_file = os.path.join(script_dir, "valid_proxies.txt")
    
    proxies = []
    try:
        if os.path.exists(proxy_file):
            with open(proxy_file, "r") as f:
                proxies = [p.strip() for p in f.readlines() if p.strip()]
    except Exception as e:
        print(f"⚠️ Failed to load proxies: {e}")
    
    return proxies

PROXY_LIST = _load_proxies()
PROXY_INDEX = 0
USE_PROXIES = False  # Set to False to test without proxies, True to enable


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
    
    def _get_next_proxy(self) -> Optional[Dict[str, str]]:
        """Get next proxy from the rotation list."""
        global PROXY_INDEX
        
        if not USE_PROXIES or not PROXY_LIST:
            return None
        
        proxy = PROXY_LIST[PROXY_INDEX % len(PROXY_LIST)]
        PROXY_INDEX += 1
        
        # Format proxy with http:// if not already included
        if not proxy.startswith('http'):
            proxy = f'http://{proxy}'
        
        return {"http": proxy, "https": proxy}
        
    def _get_chrome_options(self, proxy: Optional[str] = None) -> uc.ChromeOptions:
        """Create Chrome options with anti-detection measures and optional proxy."""
        opts = uc.ChromeOptions()
        opts.add_argument("--disable-gpu")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--disable-blink-features=AutomationControlled")
        opts.add_argument("--disable-infobars")
        opts.add_argument("--disable-extensions")
        opts.add_argument("--disable-web-security")
        
        # User agent
        opts.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")
        
        # Add proxy if provided
        if proxy:
            opts.add_argument(f"--proxy-server={proxy}")
            print(f"🌐 Using proxy: {proxy}")
        
        return opts
    
    def _create_driver(self) -> uc.Chrome:
        """Create and configure Chrome driver with enhanced anti-detection and proxy rotation."""
        try:
            # Try to create Chrome driver
            print("🔧 Initializing Chrome driver...")
            proxy = self._get_next_proxy()
            proxy_str = proxy["http"] if proxy else None
            opts = self._get_chrome_options(proxy=proxy_str)
            driver = uc.Chrome(options=opts, version_main=None, use_subprocess=True)
            
            # Additional anti-detection JavaScript
            driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
            })
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            print("✅ Chrome driver initialized successfully")
            return driver
        except Exception as e:
            print(f"⚠️ Primary driver creation failed: {e}")
            print("🔄 Trying alternative driver initialization...")
            
            try:
                # Fallback: Try without version specification
                proxy = self._get_next_proxy()
                proxy_str = proxy["http"] if proxy else None
                opts = self._get_chrome_options(proxy=proxy_str)
                driver = uc.Chrome(options=opts, use_subprocess=True)
                driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                print("✅ Alternative Chrome driver initialized successfully")
                return driver
            except Exception as e2:
                print(f"⚠️ Alternative initialization failed: {e2}")
                print("\n💡 TROUBLESHOOTING TIPS:")
                print("   1. Update Chrome browser to the latest version")
                print("   2. Clear Chrome driver cache:")
                print("      - Delete folder: C:\\Users\\{username}\\.cache\\undetected_chromedriver\\")
                print("   3. Restart your computer")
                print("   4. Try running: pip install --upgrade undetected-chromedriver")
                raise e2
    
    def _sanitize_filename(self, filename: str) -> str:
        """Remove invalid characters from filename."""
        return re.sub(r'[<>:\"/\\|?*]', '', filename)
    
    def _create_product_directory(self, product: ProductData) -> str:
        """Create directory structure for product. Skip if already exists."""
        sanitized_title = self._sanitize_filename(product.title)
        product_path = os.path.join(self.config.output_path, sanitized_title)
        
        if os.path.isdir(product_path):
            print(f"ℹ️ Directory already exists, using existing: {product_path}")
            return product_path
            
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
                proxy = self._get_next_proxy()
                response = requests.get(image_url, timeout=30, proxies=proxy)
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
    
    def _check_for_captcha(self) -> bool:
        """Check if the page is showing a CAPTCHA or bot detection."""
        try:
            page_text = self.driver.page_source.lower()
            captcha_indicators = [
                'press & hold',
                'confirm you are a human',
                'captcha',
                'are you a robot',
                'not a bot',
                'cloudflare',
                'access denied'
            ]
            
            for indicator in captcha_indicators:
                if indicator in page_text:
                    print(f"⚠️ CAPTCHA detected: {indicator}")
                    return True
            return False
        except:
            return False
    
    def scrape(self) -> ScrapingResult:
        """Main scraping method that orchestrates the entire process."""
        try:
            # Initialize driver
            self.driver = self._create_driver()
            
            # Navigate to URL
            self.driver.get(self.url)
            print(f"➡️ Navigated to: {self.url}")
            
            # Check for CAPTCHA
            if self._check_for_captcha():
                error_msg = f"CAPTCHA/Bot detection encountered for {self.url}. Skipping."
                print(f"⚠️ {error_msg}")
                return ScrapingResult(
                    success=False, 
                    error=error_msg
                )
            
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
