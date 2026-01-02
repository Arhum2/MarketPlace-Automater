"""
Generic scraper for any e-commerce site using meta tags and common patterns.
Serves as a fallback when no specific scraper is available.
"""
import re
import time
import random
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Optional, List
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

from base_scraper import BaseScraper
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
from models import ProductData


class GenericScraper(BaseScraper):
    """Generic scraper with aggressive anti-detection for heavily protected sites."""
    
    # Stealth injection scripts to bypass detection
    STEALTH_SCRIPTS = [
        # Remove navigator.webdriver
        """
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        """,
        # Override chrome property
        """
        window.chrome = {
            runtime: {}
        };
        """,
        # Mock navigator.plugins
        """
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5]
        });
        """,
        # Mock navigator.languages
        """
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en']
        });
        """,
        # Override permissions
        """
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );
        """,
        # Remove headless flag
        """
        Object.defineProperty(navigator, 'headless', {
            get: () => false
        });
        """
    ]
    
    def is_supported_url(self, url: str) -> bool:
        """Generic scraper supports all URLs as a fallback."""
        return True
    
    def _apply_stealth_scripts(self) -> None:
        """Inject stealth scripts to bypass detection."""
        print("🛡️ Applying enhanced stealth mode...")
        print("   🔨 Creating stealth Chrome instance...")
        
        for idx, script in enumerate(self.STEALTH_SCRIPTS, 1):
            try:
                self.driver.execute_script(script)
            except Exception as e:
                print(f"   ⚠️ Script {idx} failed: {e}")
        
        print(f"   🎭 Injecting anti-detection scripts...")
        print(f"   ✅ Injected {len(self.STEALTH_SCRIPTS)}/6 stealth scripts")
    
    def _simulate_human_behavior(self) -> None:
        """Simulate human browsing behavior."""
        print("🤖 Simulating human browsing behavior...")
        
        try:
            # Random scroll
            scroll_height = random.randint(3, 8)
            self.driver.execute_script(f"window.scrollBy(0, {scroll_height * 200});")
            time.sleep(random.uniform(1, 3))
            print(f"   ✅ Scrolling through page completed!")
            
            # Scroll back up
            self.driver.execute_script("window.scrollBy(0, -5000);")
            time.sleep(random.uniform(0.5, 1.5))
            print(f"   ✅ Final page positioning completed!")
            
            # Wait for content
            time.sleep(random.uniform(2, 4))
            print(f"   ✅ Waiting for page to fully load completed!")
            
        except Exception as e:
            print(f"   ⚠️ Human behavior simulation failed: {e}")
    
    def _configure_network_stealth(self) -> None:
        """Configure network-level stealth settings."""
        print("   🌐 Configuring network settings...")
        
        try:
            # Set realistic user agent via CDP
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
                "platform": "Win32",
                "userAgentMetadata": {
                    "platform": "Windows",
                    "platformVersion": "15.0.0",
                    "architecture": "x86",
                    "model": "",
                    "mobile": False
                }
            })
            print(f"   ✅ Network stealth configuration complete")
        except Exception as e:
            print(f"   ⚠️ Network config failed: {e}")
    
    def scrape(self) -> 'ScrapingResult':
        """Override scrape to grab HTML immediately before any interaction."""
        from base_scraper import ScrapingResult
        
        try:
            # Initialize driver
            self.driver = self._create_driver()
            
            # Navigate to URL WITHOUT any stealth stuff yet
            print("🌐 Navigating to target URL...")
            self.driver.get(self.url)
            time.sleep(random.uniform(1, 2))
            print(f"✅ Successfully loaded: {self.url}")
            
            # IMMEDIATELY grab HTML before any interaction
            print("📄 Grabbing page HTML immediately...")
            initial_html = self.driver.page_source
            soup = BeautifulSoup(initial_html, "html.parser")
            print(f"✅ Captured {len(initial_html)} bytes of page source")
            
            # Check for CAPTCHA in initial load (before interaction)
            print("🔍 Checking for bot detection...")
            if self._check_for_captcha():
                error_msg = f"CAPTCHA/Bot detection encountered for {self.url}. Skipping."
                print(f"⚠️ {error_msg}")
                return ScrapingResult(
                    success=False, 
                    error=error_msg
                )
            else:
                print("✅ No bot detection found, proceeding...")
            
            # Extract product data BEFORE any heavy interaction
            print("📊 Starting product data extraction from HTML...")
            product = self._extract_from_soup(soup)
            if not product:
                return ScrapingResult(success=False, error="Failed to extract product data")
            
            # Now that we have basic data, try to get images (may interact)
            print("🖼️ Attempting image extraction...")
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
    
    def _extract_from_soup(self, soup: BeautifulSoup) -> Optional[ProductData]:
        """Extract product data directly from soup (no browser interaction needed)."""
        product = ProductData()
        
        # Extract title
        print("ℹ️ Extracting title...")
        title = self._find_best_title(soup)
        if title:
            product.title = title
            print(f"✅ Found title: {product.title}")
        else:
            print("❌ Failed to find product title")
            return None
        
        # Extract description
        print("ℹ️ Extracting description...")
        description = self._find_best_description(soup)
        if description:
            product.description = description
            print(f"✅ Found description: {product.description[:100]}...")
        else:
            print("⚠️ Description not found")
        
        # Extract price
        print("ℹ️ Extracting price...")
        price = self._find_best_price(soup)
        if price:
            product.price = price
            print(f"✅ Found price: {product.price}")
        else:
            print("⚠️ Price not found")
        
        # Set link
        product.link = self.url
        
        return product
    
    def _get_meta_property(self, soup: BeautifulSoup, prop: str) -> Optional[str]:
        """Extract content from meta property or name tag."""
        # Try property attribute first (OpenGraph)
        tag = soup.find("meta", {"property": prop})
        if tag and tag.get("content"):
            return tag["content"]
        
        # Try name attribute as fallback
        tag = soup.find("meta", {"name": prop})
        if tag and tag.get("content"):
            return tag["content"]
        
        return None
    
    def _extract_price_from_text(self, text: str) -> Optional[str]:
        """Extract price from text using regex."""
        if not text:
            return None
        
        # Common price patterns: $123, $123.45, 123.45, £123
        patterns = [
            r'[\$£€][\d,]+(?:\.\d{2})?',  # Currency symbol
            r'\d+(?:\.\d{2})?(?:\s*(?:CAD|USD|EUR|GBP))?',  # Amount with currency code
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0).strip()
        
        return None
    
    def _find_best_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Find product title using multiple strategies."""
        # Strategy 1: OpenGraph
        title = self._get_meta_property(soup, "og:title")
        if title:
            return self._sanitize_filename(title)
        
        # Strategy 2: Meta description tag
        title = self._get_meta_property(soup, "title")
        if title:
            return self._sanitize_filename(title)
        
        # Strategy 3: H1 tag
        h1 = soup.find("h1")
        if h1 and h1.text.strip():
            return self._sanitize_filename(h1.text.strip())
        
        # Strategy 4: First h2
        h2 = soup.find("h2")
        if h2 and h2.text.strip():
            return self._sanitize_filename(h2.text.strip())
        
        return None
    
    def _find_best_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Find product description using multiple strategies."""
        # Strategy 1: OpenGraph description
        desc = self._get_meta_property(soup, "og:description")
        if desc:
            return desc
        
        # Strategy 2: Meta description
        desc = self._get_meta_property(soup, "description")
        if desc:
            return desc
        
        # Strategy 3: Look for common description classes/ids
        selectors = [
            'div[class*="description"]',
            'div[id*="description"]',
            'div[class*="product-info"]',
            'div[class*="details"]',
            'article',
        ]
        
        for selector in selectors:
            elem = soup.select_one(selector)
            if elem and elem.text.strip():
                text = elem.text.strip()[:500]  # Limit to 500 chars
                return text
        
        return None
    
    def _find_best_price(self, soup: BeautifulSoup) -> Optional[str]:
        """Find product price using multiple strategies."""
        # Strategy 1: Look for price in common locations
        price_selectors = [
            'span[class*="price"]',
            'span[id*="price"]',
            'div[class*="price"]',
            'p[class*="price"]',
            'span[data-price]',
        ]
        
        for selector in price_selectors:
            elem = soup.select_one(selector)
            if elem and elem.text.strip():
                price = self._extract_price_from_text(elem.text.strip())
                if price:
                    return price
        
        # Strategy 2: Search entire page for price patterns
        page_text = soup.get_text()
        price = self._extract_price_from_text(page_text)
        if price:
            return price
        
        return None
    
    def extract_product_data(self) -> Optional[ProductData]:
        """Extract product data from any e-commerce page."""
        try:
            time.sleep(random.uniform(*self.config.request_delay))
            
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            
            product = ProductData()
            
            # Extract title
            print("ℹ️ Extracting title...")
            title = self._find_best_title(soup)
            if title:
                product.title = title
                print(f"✅ Found title: {product.title}")
            else:
                print("❌ Failed to find product title")
                return None
            
            # Extract description
            print("ℹ️ Extracting description...")
            description = self._find_best_description(soup)
            if description:
                product.description = description
                print(f"✅ Found description: {product.description[:100]}...")
            else:
                print("⚠️ Description not found")
            
            # Extract price
            print("ℹ️ Extracting price...")
            price = self._find_best_price(soup)
            if price:
                product.price = price
                print(f"✅ Found price: {product.price}")
            else:
                print("⚠️ Price not found")
            
            # Set link
            product.link = self.url
            
            return product
            
        except Exception as e:
            print(f"❌ Failed to extract product data: {e}")
            return None
    
    def extract_images(self) -> List[str]:
        """Extract image URLs from the page."""
        print("🌐 [START] extract_images (generic)")
        
        try:
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            image_urls = []
            
            # Strategy 1: OpenGraph image
            og_image = self._get_meta_property(soup, "og:image")
            if og_image:
                image_urls.append(og_image)
                print(f"✅ Found OG image: {og_image[:60]}...")
            
            # Strategy 2: Twitter image
            twitter_image = self._get_meta_property(soup, "twitter:image")
            if twitter_image and twitter_image not in image_urls:
                image_urls.append(twitter_image)
                print(f"✅ Found Twitter image: {twitter_image[:60]}...")
            
            # Strategy 3: Collect all img tags
            images = soup.find_all("img")
            print(f"🔍 Found {len(images)} <img> tags")
            
            for img in images:
                if len(image_urls) >= self.config.max_images:
                    break
                
                src = img.get("src") or img.get("data-src")
                if not src:
                    continue
                
                # Skip common non-product images
                skip_patterns = [
                    'logo', 'icon', 'banner', 'button', 'pixel', 
                    'tracker', 'badge', 'social', 'nav', 'menu',
                    '1x1', 'small', 'tiny'
                ]
                
                if any(pattern in src.lower() for pattern in skip_patterns):
                    continue
                
                # Skip if already added
                if src in image_urls:
                    continue
                
                # Prefer images with reasonable dimensions in URL
                if any(indicator in src for indicator in ['.jpg', '.jpeg', '.png', '.webp']):
                    image_urls.append(src)
                    print(f"  ✅ Added image: {src[:60]}...")
            
            print(f"✅ Found {len(image_urls)} images")
            print("🌐 [END] extract_images")
            return image_urls
            
        except Exception as e:
            print(f"❌ Failed to extract images: {e}")
            return []
