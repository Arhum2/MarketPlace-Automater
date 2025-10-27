"""
Amazon-specific scraper implementation.
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


class AmazonScraper(BaseScraper):
    """Amazon-specific scraper implementation."""
    
    SUPPORTED_DOMAINS = ['amazon.com', 'amazon.ca', 'amazon.co.uk']
    
    # Selector configurations
    TITLE_SELECTORS = [
        {"type": "id", "value": "productTitle"},
        {"type": "id", "value": "title"},
    ]
    
    PRICE_SELECTORS = [
        {"type": "class", "value": "a-price-whole"},
        {"type": "class", "value": "a-price"},
    ]
    
    DESCRIPTION_SELECTORS = [
        {"type": "id", "value": "featureBulletsAndDescription_hoc_feature_div"},
        {"type": "id", "value": "feature-bullets"},
    ]
    
    def is_supported_url(self, url: str) -> bool:
        """Check if URL is from a supported Amazon domain."""
        return any(domain in url.lower() for domain in self.SUPPORTED_DOMAINS)
    
    def _find_element_by_selectors(self, selectors: List[dict], timeout: int = 10) -> Optional[str]:
        """Try multiple selectors to find an element."""
        for selector_config in selectors:
            try:
                if selector_config["type"] == "id":
                    element = WebDriverWait(self.driver, timeout).until(
                        EC.presence_of_element_located((By.ID, selector_config["value"]))
                    )
                elif selector_config["type"] == "class":
                    element = WebDriverWait(self.driver, timeout).until(
                        EC.presence_of_element_located((By.CLASS_NAME, selector_config["value"]))
                    )
                elif selector_config["type"] == "css":
                    element = WebDriverWait(self.driver, timeout).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector_config["value"]))
                    )
                
                if element and element.text.strip():
                    return element.text.strip()
                    
            except Exception as e:
                print(f"⚠️ Selector {selector_config} failed: {e}")
                continue
                
        return None
    
    def extract_product_data(self) -> Optional[ProductData]:
        """Extract product data from Amazon product page."""
        try:
            self.driver.maximize_window()
            
            # Wait for page to load - give Amazon more time
            time.sleep(5)
            
            product = ProductData()
            
            # Extract title
            print("ℹ️ Extracting title...")
            title = self._find_element_by_selectors(self.TITLE_SELECTORS, timeout=15)
            if title:
                product.title = self._sanitize_filename(title)
                print(f"✅ Found title: {product.title}")
            else:
                print("❌ Failed to find product title")
                return None
            
            # Extract price
            print("ℹ️ Extracting price...")
            price = self._find_element_by_selectors(self.PRICE_SELECTORS, timeout=15)
            if price:
                product.price = price
                print(f"✅ Found price: {product.price}")
            else:
                print("⚠️ Price not found")
            
            # Extract description
            print("ℹ️ Extracting description...")
            description = self._find_element_by_selectors(self.DESCRIPTION_SELECTORS, timeout=15)
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
        """Extract image URLs from Amazon product page."""
        print("🌐 [START] extract_images")
        
        try:
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            images = soup.find_all("img")
            image_urls = []
            
            for img in images:
                src = img.get("src") or img.get("data-src")
                if not src:
                    continue
                
                # Amazon-specific image identification
                is_main = img.get("id") == 'main-image'
                is_alt = img.get("data-a-image-name") == 'altImage'
                is_product_image = any(indicator in src for indicator in ['.jpg', '.jpeg', '.png'])
                
                if is_main or is_alt or is_product_image:
                    # Convert to high resolution if possible
                    if '_SL' in src or '_AC_' in src:
                        # Replace size indicators with larger ones
                        src = re.sub(r'_SL\d+_', '_SL1500_', src)
                        src = re.sub(r'_AC_.*?_', '_AC_SL1500_', src)
                    
                    image_urls.append(src)
                    
                if len(image_urls) >= self.config.max_images:
                    break
            
            print(f"✅ Found {len(image_urls)} images")
            print("🌐 [END] extract_images")
            return image_urls
            
        except Exception as e:
            print(f"❌ Failed to extract images: {e}")
            return []
