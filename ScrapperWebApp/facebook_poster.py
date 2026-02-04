"""
Facebook Marketplace Poster

Posts products to Facebook Marketplace using Selenium and PyAutoGUI.
"""

import os
import shutil
import requests
from time import sleep
from datetime import datetime
from typing import List, Dict, Any, Optional

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from dotenv import load_dotenv
from database import get_db

load_dotenv()

# Configuration from environment
TEMP_FOLDER = os.getenv("TEMP_IMAGE_FOLDER", "C:\\temp\\fb_posting")
CHROME_PROFILE = os.getenv("CHROME_PROFILE_PATH", "C:\\ChromeProfiles\\FBProfile")
MARKETPLACE_URL = "https://www.facebook.com/marketplace/create/item"


def download_images(product_id: str) -> List[str]:
    """
    Download product images from Supabase to temp folder.
    Returns list of local file paths.
    """
    db = get_db()
    images = db.get_product_images(product_id)

    if not images:
        print(f"No images found for product {product_id}")
        return []

    # Create product-specific temp folder
    product_temp_folder = os.path.join(TEMP_FOLDER, product_id)
    os.makedirs(product_temp_folder, exist_ok=True)

    local_paths = []

    for i, img in enumerate(images):
        file_url = img.get('file_path', '')
        if not file_url:
            continue

        try:
            # Download the image
            response = requests.get(file_url, timeout=30)
            response.raise_for_status()

            # Save locally
            filename = f"image_{i}.jpg"
            local_path = os.path.join(product_temp_folder, filename)

            with open(local_path, 'wb') as f:
                f.write(response.content)

            local_paths.append(local_path)
            print(f"Downloaded: {local_path}")

        except Exception as e:
            print(f"Failed to download image {i}: {e}")

    return local_paths


def cleanup_temp_images(product_id: str) -> bool:
    """
    Delete temp images for a product after posting.
    """
    product_temp_folder = os.path.join(TEMP_FOLDER, product_id)

    try:
        if os.path.exists(product_temp_folder):
            shutil.rmtree(product_temp_folder)
            print(f"Cleaned up temp folder: {product_temp_folder}")
        return True
    except Exception as e:
        print(f"Failed to cleanup temp folder: {e}")
        return False


def setup_browser() -> webdriver.Chrome:
    """
    Set up Chrome browser with persistent profile for Facebook login.
    """
    service = Service(ChromeDriverManager().install())

    opts = Options()
    opts.add_argument("--disable-gpu")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--disable-infobars")
    opts.add_argument("--disable-extensions")
    opts.add_argument(f"--user-data-dir={CHROME_PROFILE}")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)

    browser = webdriver.Chrome(service=service, options=opts)
    return browser


def post_to_facebook(product_id: str) -> Dict[str, Any]:
    """
    Post a product to Facebook Marketplace.

    Returns dict with success status and any error message.
    """
    db = get_db()
    product = db.get_product(product_id)

    if not product:
        return {"success": False, "error": "Product not found"}

    # Check required fields
    if not product.get('title') or not product.get('price'):
        return {"success": False, "error": "Product missing title or price"}

    print(f"Starting Facebook post for: {product.get('title')}")

    # Step 1: Download images
    print("Downloading images...")
    image_paths = download_images(product_id)

    if not image_paths:
        return {"success": False, "error": "No images to upload"}

    browser = None

    try:
        # Step 2: Set up browser and navigate to Marketplace
        print("Opening browser...")
        browser = setup_browser()
        browser.get(MARKETPLACE_URL)
        sleep(5)  # Wait for page to load

        # Step 3: Upload images using file input
        print("Uploading images...")
        try:
            # Find the file input by stable attributes
            file_input = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="file"][accept*="image"]'))
            )

            # Send all file paths (joined with newlines for multiple files)
            file_paths_str = "\n".join(image_paths)
            file_input.send_keys(file_paths_str)
            print(f"Uploaded {len(image_paths)} images via file input")
            sleep(3)  # Wait for upload

        except Exception as e:
            print(f"File input method failed: {e}")
            return {"success": False, "error": f"Failed to upload images: {e}"}

        # Step 4: Fill form fields using Selenium (stable XPath selectors)
        print("Filling form fields...")

        # Title (truncate to 99 chars for Facebook limit)
        try:
            title_input = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.XPATH, '//label[.//span[text()="Title"]]//input'))
            )
            title = product.get('title', '')[:99]  # Truncate to Facebook's 99 char limit
            title_input.send_keys(title)
            print(f"Filled title: {title}")
            sleep(1)
        except Exception as e:
            print(f"Failed to fill title: {e}")
            return {"success": False, "error": f"Failed to fill title: {e}"}

        # Price
        try:
            price_input = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.XPATH, '//label[.//span[text()="Price"]]//input'))
            )
            # Remove any non-numeric characters from price
            price = ''.join(filter(str.isdigit, str(product.get('price', '0'))))
            price_input.send_keys(price)
            print(f"Filled price: {price}")
            sleep(1)
        except Exception as e:
            print(f"Failed to fill price: {e}")
            return {"success": False, "error": f"Failed to fill price: {e}"}

        # Category - Select "Furniture"
        try:
            print("Selecting category: Furniture")
            # Find Category dropdown - it's a <label> element with role="combobox"
            category_dropdown = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.XPATH, '//label[@role="combobox"][.//span[text()="Category"]]'))
            )
            browser.execute_script("arguments[0].scrollIntoView(true);", category_dropdown)
            sleep(1)

            # Click the dropdown
            category_dropdown.click()
            print("Clicked Category dropdown")
            sleep(3)  # Wait for dropdown to fully open

            # Find and click "Furniture" option in the listbox
            furniture_option = WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//div[@role="listbox"]//span[text()="Furniture"] | //span[text()="Furniture"]'))
            )
            browser.execute_script("arguments[0].scrollIntoView(true);", furniture_option)
            sleep(0.5)
            furniture_option.click()
            print("Selected Furniture")
            sleep(2)
        except Exception as e:
            print(f"Failed to select category: {type(e).__name__}: {e}")
            import traceback
            print(traceback.format_exc())
            # Don't fail the whole post
            pass

        # Condition - Select "New"
        try:
            print("Selecting condition: New")
            # Find Condition dropdown - it's a <label> element with role="combobox"
            condition_dropdown = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.XPATH, '//label[@role="combobox"][.//span[text()="Condition"]]'))
            )
            browser.execute_script("arguments[0].scrollIntoView(true);", condition_dropdown)
            sleep(1)

            # Click the dropdown
            condition_dropdown.click()
            print("Clicked Condition dropdown")
            sleep(3)  # Wait for dropdown to fully open

            # Find and click "New" option in the listbox
            new_option = WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//div[@role="listbox"]//span[text()="New"] | //div[@role="option"]//span[text()="New"] | //span[text()="New"]'))
            )
            browser.execute_script("arguments[0].scrollIntoView(true);", new_option)
            sleep(0.5)
            new_option.click()
            print("Selected New")
            sleep(2)
        except Exception as e:
            print(f"Failed to select condition: {type(e).__name__}: {e}")
            import traceback
            print(traceback.format_exc())
            # Don't fail the whole post
            pass

        # Description
        try:
            description_input = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.XPATH, '//label[.//span[text()="Description"]]//textarea | //label[.//span[text()="Description"]]//input'))
            )
            description = product.get('description', '')
            if description:
                description_input.send_keys(description[:500])  # Limit to 500 chars
                description_input.send_keys('\n')  # Press enter
                description_input.send_keys('\n')  # Press enter
                description_input.send_keys('Here is a link to the original product: ')  # Press enter
                description_input.send_keys(product.get('url', ''))  # Add source URL
            print(f"Filled description")
            sleep(2)
        except Exception as e:
            print(f"Failed to fill description: {e}")
            # Don't fail the whole post for description
            pass

        sleep(3)  # Wait for everything to settle

        # Step 5: Save as draft
        print("Saving draft...")
        try:
            save_button = browser.find_element(By.XPATH, '//span[text()="Save draft"]')
            save_button.click()
            sleep(3)
        except Exception as e:
            print(f"Could not click Save draft button: {e}")
            # Continue anyway - user can manually save

        # Step 6: Update product status in database
        print("Updating product status...")
        db.update_product(
            product_id,
            status="posted",
            posted_at=datetime.utcnow().isoformat()
        )

        # Step 7: Cleanup temp images
        print("Cleaning up temp files...")
        cleanup_temp_images(product_id)

        print(f"Successfully posted product: {product.get('title')}")
        return {"success": True, "message": "Product posted to Facebook (saved as draft)"}

    except Exception as e:
        print(f"Error posting to Facebook: {e}")
        return {"success": False, "error": str(e)}

    finally:
        if browser:
            sleep(2)
            browser.quit()


# For testing
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        product_id = sys.argv[1]
        result = post_to_facebook(product_id)
        print(f"Result: {result}")
    else:
        print("Usage: python facebook_poster.py <product_id>")