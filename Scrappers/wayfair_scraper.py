"""
Wayfair-specific scraper implementation.
"""
import re
import time
import random
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Optional, List
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

from base_scraper import BaseScraper
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
from models import ProductData


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
            
            for img in images:
                src = img.get("src") or img.get("data-src")
                if not src:
                    continue
                
                # Wayfair-specific image identification
                is_h800 = "h800" in src
                is_initial = img.get("data-enzyme-id") == "InitialImage"
                is_product_image = any(indicator in src for indicator in ['.jpg', '.jpeg', '.png', '.webp'])
                
                if is_h800 or is_initial or is_product_image:
                    # Convert to higher resolution if possible
                    if 'resize=h800' in src:
                        src = src.replace('resize=h800', 'resize=h1200')
                    
                    image_urls.append(src)
                    
                if len(image_urls) >= self.config.max_images:
                    break
            
            print(f"✅ Found {len(image_urls)} images")
            print("🌐 [END] extract_images")
            return image_urls
            
        except Exception as e:
            print(f"❌ Failed to extract images: {e}")
            return []
