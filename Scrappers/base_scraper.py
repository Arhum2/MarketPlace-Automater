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


class ScraperConfig:
    """Configuration class for scraper settings."""
    
    def __init__(self, 
                 output_path: str = "G:\\My Drive\\selling\\not posted\\",
                 max_images: int = 10,
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
        
    def _get_chrome_options(self) -> uc.ChromeOptions:
        """Create Chrome options with enhanced anti-detection measures."""
        opts = uc.ChromeOptions()
        
        # Basic stealth options
        opts.add_argument("--disable-gpu")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--disable-blink-features=AutomationControlled")
        opts.add_argument("--disable-infobars")
        opts.add_argument("--disable-extensions")
        opts.add_argument("--disable-web-security")
        
        # Enhanced anti-detection for Wayfair
        if 'wayfair' in self.url.lower():
            print("🔧 Applying enhanced Wayfair anti-detection...")
            opts.add_argument("--disable-features=VizDisplayCompositor")
            opts.add_argument("--disable-ipc-flooding-protection")
            opts.add_argument("--disable-renderer-backgrounding")
            opts.add_argument("--disable-backgrounding-occluded-windows")
            opts.add_argument("--disable-background-networking")
            opts.add_argument("--disable-background-timer-throttling")
            opts.add_argument("--disable-client-side-phishing-detection")
            opts.add_argument("--disable-default-apps")
            opts.add_argument("--disable-hang-monitor")
            opts.add_argument("--disable-popup-blocking")
            opts.add_argument("--disable-prompt-on-repost")
            opts.add_argument("--disable-sync")
            opts.add_argument("--disable-translate")
            opts.add_argument("--metrics-recording-only")
            opts.add_argument("--safebrowsing-disable-auto-update")
            opts.add_argument("--enable-automation")
            opts.add_argument("--password-store=basic")
            opts.add_argument("--use-mock-keychain")
            
            # Window size to appear more human
            opts.add_argument("--window-size=1366,768")
            
            # More realistic user agent
            opts.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36")
        else:
            # Standard user agent for non-Wayfair sites
            opts.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")
        
        return opts
    
    def _create_driver(self) -> uc.Chrome:
        """Create and configure Chrome driver with enhanced anti-detection."""
        try:
            print("🔧 Initializing Chrome driver...")
            opts = self._get_chrome_options()
            
            # Enhanced driver creation for Wayfair
            if 'wayfair' in self.url.lower():
                print("🛡️ Applying enhanced Wayfair stealth mode...")
                print("   🔨 Creating stealth Chrome instance...")
                driver = uc.Chrome(
                    options=opts, 
                    version_main=None, 
                    use_subprocess=True,
                    suppress_welcome=True
                )
                
                print("   🎭 Injecting anti-detection scripts...")
                # Execute multiple anti-detection scripts for Wayfair
                stealth_scripts = [
                    "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})",
                    "Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})",
                    "Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})",
                    "Object.defineProperty(navigator, 'permissions', {get: () => ({query: () => Promise.resolve({state: 'granted'})})})",
                    "window.chrome = {runtime: {}};",
                    "delete navigator.__proto__.webdriver;"
                ]
                
                script_count = 0
                for script in stealth_scripts:
                    try:
                        driver.execute_script(script)
                        script_count += 1
                    except:
                        pass
                print(f"   ✅ Injected {script_count}/{len(stealth_scripts)} stealth scripts")
                
                # Set additional CDP commands for Wayfair
                print("   🌐 Configuring network settings...")
                try:
                    driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                        "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
                        "platform": 'Win32'
                    })
                    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                        "source": """
                        Object.defineProperty(navigator, 'webdriver', {
                            get: () => undefined,
                        });
                        """
                    })
                    print("   ✅ Network stealth configuration complete")
                except:
                    pass
                    
            else:
                # Standard driver for other sites
                driver = uc.Chrome(options=opts, version_main=None, use_subprocess=True)
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
                opts = self._get_chrome_options()
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
    
    def _progress_sleep(self, duration: float, message: str = "Waiting"):
        """Sleep with progress countdown display."""
        total_seconds = int(duration)
        print(f"⏳ {message} ({total_seconds}s)", end="", flush=True)
        
        # Only show countdown if duration is more than 1 second
        if total_seconds > 0:
            for remaining in range(total_seconds, 0, -1):
                print(f"\r⏳ {message} ({remaining}s)" + "." * (total_seconds - remaining + 1), end="", flush=True)
                time.sleep(1)
        
        # Handle fractional seconds
        fractional = duration - total_seconds
        if fractional > 0:
            time.sleep(fractional)
        
        print(f"\r✅ {message} completed!" + " " * 30)  # Clear the line
        print()  # New line for next output
    
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
    
    def _check_for_captcha(self) -> bool:
        """Check if the page is showing a CAPTCHA or bot detection."""
        try:
            page_text = self.driver.page_source.lower()
            
            # More specific CAPTCHA indicators that indicate actual blocking
            strong_captcha_indicators = [
                'press & hold',
                'confirm you are a human',
                'verify you are human',
                'are you a robot',
                'not a robot',
                'i am not a robot',
                'please verify',
                'human verification',
                'access denied',
                'blocked'
            ]
            
            # Check for strong indicators first
            for indicator in strong_captcha_indicators:
                if indicator in page_text:
                    print(f"⚠️ CAPTCHA detected: {indicator}")
                    return True
            
            # Check for Cloudflare challenge page specifically
            if 'cloudflare' in page_text and ('challenge' in page_text or 'checking' in page_text):
                print(f"⚠️ CAPTCHA detected: cloudflare challenge")
                return True
            
            # For Wayfair, be more lenient - only check for obvious blocking pages
            if 'wayfair' in self.url.lower():
                # Only flag as CAPTCHA if we see very specific blocking indicators
                wayfair_blocking_indicators = [
                    'access denied',
                    'blocked',
                    'please verify you are human',
                    'robot verification'
                ]
                for indicator in wayfair_blocking_indicators:
                    if indicator in page_text:
                        print(f"⚠️ Wayfair CAPTCHA detected: {indicator}")
                        return True
                return False
            
            # Check if the page title indicates a blocking page
            try:
                page_title = self.driver.title.lower()
                if any(blocked_title in page_title for blocked_title in ['blocked', 'access denied', 'captcha', 'verification']):
                    print(f"⚠️ CAPTCHA detected: blocking page title")
                    return True
            except:
                pass
            
            return False
        except:
            return False
    
    def scrape(self) -> ScrapingResult:
        """Main scraping method that orchestrates the entire process."""
        try:
            # Initialize driver
            self.driver = self._create_driver()
            
            # Navigate to URL
            print(f"🌐 Navigating to target URL...")
            self.driver.get(self.url)
            print(f"✅ Successfully loaded: {self.url}")
            
            # Check for CAPTCHA - Disabled for Wayfair during testing
            print("🔍 Checking for bot detection...")
            if 'wayfair' not in self.url.lower() and self._check_for_captcha():
                error_msg = f"CAPTCHA/Bot detection encountered for {self.url}. Skipping."
                print(f"⚠️ {error_msg}")
                return ScrapingResult(
                    success=False, 
                    error=error_msg
                )
            print("✅ No bot detection found, proceeding...")
            
            # Extract product data
            print("📊 Starting product data extraction...")
            product = self.extract_product_data()
            if not product:
                print("❌ Product data extraction failed")
                return ScrapingResult(success=False, error="Failed to extract product data")
            print("✅ Product data extraction complete")
            
            # Extract images  
            print("🖼️ Starting image extraction...")
            self.images = self.extract_images()
            print(f"✅ Found {len(self.images)} images")
            
            # Create directory and save data
            print("📁 Creating product directory structure...")
            product_path = self._create_product_directory(product)
            print(f"✅ Created directory: {product_path}")
            
            print("💾 Saving product information...")
            self._save_product_info(product, product_path)
            print("✅ Product info saved")
            
            print("⬇️ Downloading images...")
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
