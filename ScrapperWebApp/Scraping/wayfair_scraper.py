"""
Wayfair-specific scraper implementation.
"""
import re
import time
import random

from typing import Optional, List
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

from .base_scraper import BaseScraper, ScrapingResult
from .models import ProductData


class WayfairScraper(BaseScraper):
    """Wayfair-specific scraper implementation."""
    
    SUPPORTED_DOMAINS = ['wayfair.com', 'wayfair.ca']
    
    # Selector configurations
    TITLE_SELECTORS = [
        {"type": "css", "value": "._6o3atz174.hapmhk7.hapmhkf.hapmhkl"},
        {"type": "css", "value": "h1[data-test-id='product-title']"},
    ]
    
    PRICE_SELECTORS = [
        {"type": "css", "value": "[data-test-id='product-price']"},
        {"type": "css", "value": "._6o3atzbl._6o3atzc7._6o3atz19j"},
        {"type": "css", "value": "._1fat8tg5h._1fat8tg2f._1fat8tg13e._1fat8tg174._1fat8tgbl"},
        {"type": "xpath", "value": "//span[contains(@class, 'price') or contains(text(), '$')]"},
        {"type": "css", "value": ".ProductDetailInfoV2-module__price"},
        {"type": "css", "value": "[class*='price']"},
        {"type": "xpath", "value": "/html/body/div[2]/div[2]/div[1]/div[2]/div/div[2]/div[2]/div/div/div/div[1]/div/span/span/span/span/span"}
    ]
    
    DESCRIPTION_SELECTORS = [
        {"type": "class", "value": "_1dufoct2"},
        {"type": "class", "value": "RomanceCopy-text"},
    ]
    
    EXPANDABLE_SELECTORS = [
        {"type": "css", "value": "#react-collapsed-toggle-\\:R8qml9j7rn7mkq\\:"},
        {"type": "css", "value": "#react-collapsed-panel-\\:R4qml9j7rn7mkq\\: > div._1dufoctg > button"},
        {"type": "css", "value": "._1pmvkjd1._1pmvkjd2._1pmvkjd6._1pmvkjd9._1pmvkjdw"},
        {"type": "xpath", "value": "//button[.//p[text()='Specifications']]"},
        {"type": "xpath", "value": "//button[.//span[text()[contains(translate(., 'SHOW MORE', 'show more'), 'show more')]]]"},
    ]
    
    def is_supported_url(self, url: str) -> bool:
        """Check if URL is from a supported Wayfair domain."""
        return any(domain in url.lower() for domain in self.SUPPORTED_DOMAINS)
    
    def _get_meta_property(self, soup: BeautifulSoup, prop: str) -> Optional[str]:
        """Extract content from meta property tag."""
        tag = soup.find("meta", {"property": prop})
        return tag["content"] if tag else None
    
    def scrape(self):
        """Override scrape method with aggressive anti-detection for Wayfair."""
        try:
            # Create driver with anti-detection
            self.driver = self._create_driver()
            
            # Apply AGGRESSIVE stealth BEFORE navigation
            print("🛡️ Applying pre-navigation stealth techniques...")
            self._apply_stealth_scripts_before_nav()
            
            # NOW navigate
            print(f"🌐 Navigating to {self.url}...")
            self.driver.get(self.url)
            print(f"✅ Successfully loaded: {self.url}")
            
            # Immediately grab initial HTML (BEFORE CAPTCHA JavaScript runs)
            print("📄 Grabbing initial page HTML immediately...")
            initial_html = self.driver.page_source
            soup = BeautifulSoup(initial_html, "html.parser")
            print(f"✅ Captured {len(initial_html)} bytes of initial page source")
            
            # Try to extract product data from INITIAL HTML (before CAPTCHA takes over)
            print("📊 Attempting quick extraction from initial HTML...")
            product = self._extract_from_initial_html(soup)
            
            if product and product.title:
                print(f"✅ Successfully extracted from initial HTML: {product.title}")
                
                # Get images and save
                self.images = self.extract_images()
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
            else:
                print("⚠️ Could not extract from initial HTML, trying with full extraction...")
            
            # If initial extraction failed, check for CAPTCHA
            print("🔍 Checking for bot detection...")
            if self._check_for_captcha():
                error_msg = f"CAPTCHA/Bot detection encountered for {self.url}. Trying aggressive bypass..."
                print(f"⚠️ {error_msg}")
                
                # Try aggressive bypass
                print("🔥 Applying AGGRESSIVE bypass techniques...")
                self._apply_aggressive_wayfair_bypass()
                
                # Re-check after bypass
                time.sleep(3)
                if self._check_for_captcha():
                    print("❌ Bypass failed, giving up on this URL")
                    return ScrapingResult(
                        success=False,
                        error="CAPTCHA detection could not be bypassed for " + self.url
                    )
            
            print("✅ No bot detection (or bypassed), proceeding with full extraction...")
            
            # Extract product data with full methods
            product = self.extract_product_data()
            if not product:
                return ScrapingResult(success=False, error="Failed to extract product data")
            
            # Get images
            self.images = self.extract_images()
            
            # Save data
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
    
    def _extract_from_initial_html(self, soup: BeautifulSoup) -> Optional[ProductData]:
        """Quick extraction from initial HTML using meta tags and basic selectors."""
        print("  🏃 Using fast meta tag extraction...")
        product = ProductData()
        
        # Try meta tags first (fastest)
        title = self._get_meta_property(soup, "og:title")
        if not title:
            title = self._get_meta_property(soup, "product:title")
        if not title:
            # Try basic H1
            h1 = soup.find("h1")
            if h1:
                title = h1.get_text(strip=True)
        
        if not title:
            print("  ❌ No title found in initial HTML")
            return None
        
        product.title = self._sanitize_filename(title)
        print(f"  ✅ Title: {product.title[:60]}...")
        
        # Get price from meta
        price = self._get_meta_property(soup, "product:price:amount")
        if not price:
            price = self._get_meta_property(soup, "og:price")
        if price:
            product.price = price
            print(f"  ✅ Price: {product.price}")
        
        # Get description from meta
        description = self._get_meta_property(soup, "og:description")
        if description:
            product.description = description
            print(f"  ✅ Description: {description[:50]}...")
        
        product.link = self.url
        return product
    
    def _apply_stealth_scripts_before_nav(self) -> None:
        """Apply stealth scripts BEFORE navigating to Wayfair."""
        # Apply network masking first
        try:
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                "platform": "Win32",
                "userAgentMetadata": {
                    "platformVersion": "10.0.0",
                    "fullVersion": "120.0.0.0",
                }
            })
        except:
            pass
        
        # Block tracking/detection signals
        try:
            self.driver.execute_cdp_cmd('Network.setBlockedURLs', {
                'urls': ['*://*analytics*', '*://*tracking*', '*://*detect*bot*']
            })
        except:
            pass
        
        stealth_scripts = [
            # Override navigator.webdriver
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})",
            
            # Override chrome property
            "window.chrome = {runtime: {}}",
            
            # Override plugins with realistic content
            "Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]})",
            "Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})",
            
            # Override permissions
            "const originalQuery = window.navigator.permissions.query; window.navigator.permissions.query = (parameters) => (parameters.name === 'notifications' ? Promise.resolve({state: Notification.permission}) : originalQuery(parameters));",
            
            # Remove headless indicator
            "Object.defineProperty(navigator, 'headless', {get: () => false})",
            
            # Hide undetected-chromedriver markers
            "delete navigator.__proto__.webdriver;",
            "Object.defineProperty(navigator, 'maxTouchPoints', {get: () => 10});",
        ]
        
        for script in stealth_scripts:
            try:
                self.driver.execute_script(script)
            except:
                pass
    
    def _apply_aggressive_wayfair_bypass(self) -> None:
        """Apply aggressive techniques to bypass Wayfair CAPTCHA."""
        try:
            # Add more human-like behavior
            print("  🤖 Simulating human behavior...")
            import random
            
            # Random scrolling
            for _ in range(3):
                scroll_height = random.randint(100, 500)
                self.driver.execute_script(f"window.scrollBy(0, {scroll_height})")
                time.sleep(random.uniform(1, 3))
            
            # Random mouse movements via JavaScript
            self.driver.execute_script("""
                const event = new MouseEvent('mousemove', {
                    view: window,
                    bubbles: true,
                    cancelable: true,
                    clientX: Math.random() * window.innerWidth,
                    clientY: Math.random() * window.innerHeight
                });
                document.dispatchEvent(event);
            """)
            
            # Wait with random delay
            time.sleep(random.uniform(2, 4))
            
            # Attempt to focus on page elements
            try:
                self.driver.execute_script("document.querySelector('body').click()")
            except:
                pass
                
            time.sleep(random.uniform(1, 2))
            
        except Exception as e:
            print(f"  ⚠️ Bypass technique failed: {e}")

    def _expand_panels(self) -> None:
        """Expand all collapsible panels on the page."""
        print("🔧 Expanding panels...")
        
        for selector_config in self.EXPANDABLE_SELECTORS:
            try:
                if selector_config["type"] == "css":
                    element = WebDriverWait(self.driver, 2).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector_config["value"]))
                    )
                elif selector_config["type"] == "xpath":
                    element = WebDriverWait(self.driver, 2).until(
                        EC.element_to_be_clickable((By.XPATH, selector_config["value"]))
                    )
                
                element.click()
                print(f'✅ Expanded panel: {selector_config["value"][:50]}...')
                time.sleep(0.5)  # Brief pause between clicks
                
            except Exception:
                # It's normal for some panels to not exist
                continue
    
    def _find_element_by_selectors(self, selectors: List[dict], timeout: int = 5) -> Optional[str]:
        """Try multiple selectors to find an element."""
        for selector_config in selectors:
            try:
                if selector_config["type"] == "css":
                    element = WebDriverWait(self.driver, timeout).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector_config["value"]))
                    )
                elif selector_config["type"] == "class":
                    element = WebDriverWait(self.driver, timeout).until(
                        EC.presence_of_element_located((By.CLASS_NAME, selector_config["value"]))
                    )
                elif selector_config["type"] == "id":
                    element = WebDriverWait(self.driver, timeout).until(
                        EC.presence_of_element_located((By.ID, selector_config["value"]))
                    )
                
                if element and element.text.strip():
                    return element.text.strip()
                    
            except Exception:
                continue
                
        return None
    
    def extract_product_data(self) -> Optional[ProductData]:
        """Extract product data from Wayfair product page."""
        try:
            # Enhanced stealth behavior for Wayfair
            print("🛡️ Applying Wayfair stealth techniques...")
            
            # Simulate human-like behavior - random mouse movements and scrolling
            try:
                print("🤖 Simulating human browsing behavior...")
                # Random scroll to simulate reading
                self.driver.execute_script("window.scrollTo(0, Math.floor(Math.random() * 500));")
                self._progress_sleep(random.uniform(1, 3), "Reading page content")
                
                # Scroll to middle of page
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
                self._progress_sleep(random.uniform(1, 2), "Scrolling through page")
                
                # Scroll back up a bit
                self.driver.execute_script("window.scrollTo(0, Math.floor(Math.random() * 300));")
                self._progress_sleep(random.uniform(1, 2), "Final page positioning")
            except:
                pass
            
            # Extended wait for Wayfair page to fully load
            wait_time = random.uniform(5, 8)
            self._progress_sleep(wait_time, "Waiting for Wayfair page to fully load")
            
            # Expand all panels for better data extraction
            self._expand_panels()
            
            # Additional wait after expanding panels
            self._progress_sleep(random.uniform(2, 4), "Processing expanded panels")
            
            # Get page source for fallback meta tag extraction
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            
            product = ProductData()
            
            # Extract title with longer timeout
            print("ℹ️ Extracting title...")
            title = self._find_element_by_selectors(self.TITLE_SELECTORS, timeout=15)
            if not title:
                # Fallback to meta tags
                title = self._get_meta_property(soup, "og:title")
            
            if title:
                product.title = self._sanitize_filename(title)
                print(f"✅ Found title: {product.title}")
            else:
                print("❌ Failed to find product title")
                return None
            
            # Extract price with shorter timeout to avoid hanging
            print("ℹ️ Extracting price...")
            price = self._find_element_by_selectors(self.PRICE_SELECTORS, timeout=5)
            if price:
                product.price = price
                print(f"✅ Found price: {product.price}")
            else:
                print("⚠️ Price not found")
            
            # Extract description with shorter timeout  
            print("ℹ️ Extracting description...")
            description = self._find_element_by_selectors(self.DESCRIPTION_SELECTORS, timeout=5)
            if not description:
                # Fallback to meta tags
                description = self._get_meta_property(soup, "og:description")
            
            if description:
                product.description = description
                print(f"✅ Found description: {product.description[:100]}...")
            else:
                print("⚠️ Description not found")
            
            # Set link
            product.link = self.url
            
            return product
            
        except Exception as e:
            print(f"❌ Failed to extract product data: {e}")
            return None
    
    def extract_images(self) -> List[str]:
        """Extract image URLs from Wayfair product page."""
        print("🌐 [START] extract_images")
        
        try:
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            images = soup.find_all("img")
            image_urls = []
            
            # DEBUG: Show what we found
            print(f"🔍 [DEBUG] Total <img> tags found: {len(images)}")
            
            for idx, img in enumerate(images):
                src = img.get("src") or img.get("data-src")
                if not src:
                    continue
                
                # DEBUG: Show all image sources
                print(f"  📸 Image {idx}: {src[:80]}...")
                
                # Wayfair-specific image identification
                is_h800 = "h800" in src
                is_initial = img.get("data-enzyme-id") == "InitialImage"
                is_product_image = any(indicator in src for indicator in ['.jpg', '.jpeg', '.png', '.webp'])
                
                print(f"     ├─ h800={is_h800}, initial={is_initial}, product_img={is_product_image}")
                
                if is_h800 or is_initial or is_product_image:
                    # Convert to higher resolution if possible
                    if 'resize=h800' in src:
                        src = src.replace('resize=h800', 'resize=h1200')
                    
                    image_urls.append(src)
                    print(f"     └─ ✅ ADDED (count: {len(image_urls)})")
                    
                if len(image_urls) >= self.config.max_images:
                    print(f"🛑 Reached max_images limit: {self.config.max_images}")
                    break
            
            print(f"✅ Found {len(image_urls)} images (max allowed: {self.config.max_images})")
            print("🌐 [END] extract_images")
            return image_urls
            
        except Exception as e:
            print(f"❌ Failed to extract images: {e}")
            return []
