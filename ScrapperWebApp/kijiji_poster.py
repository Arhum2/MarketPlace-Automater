"""
Kijiji Poster

Posts products to Kijiji using Selenium + undetected_chromedriver.
Mirrors the facebook_poster.py structure.
"""

import os
import re
import shutil
import requests
import subprocess
import traceback
from time import sleep
from datetime import datetime
from typing import List, Dict, Any

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

from dotenv import load_dotenv
from database import get_db

load_dotenv()

TEMP_FOLDER    = os.getenv("TEMP_IMAGE_FOLDER", "C:\\temp\\kijiji_posting")
CHROME_PROFILE = os.getenv("CHROME_PROFILE_PATH", "C:\\ChromeProfiles\\FBProfile")
POST_URL = "https://www.kijiji.ca/p-select-category.html"


# ─── Image helpers ────────────────────────────────────────────────────────────

def download_images(product_id: str) -> List[str]:
    """Download product images from Supabase to a local temp folder."""
    print(f"[Kijiji] Fetching image records for product {product_id}...")
    db = get_db()
    images = db.get_product_images(product_id)

    if not images:
        print("[Kijiji] No images found in DB.")
        return []

    product_temp = os.path.join(TEMP_FOLDER, product_id)
    os.makedirs(product_temp, exist_ok=True)
    print(f"[Kijiji] Temp folder: {product_temp}")

    local_paths = []
    for i, img in enumerate(images):
        file_url = img.get('file_path', '')
        if not file_url:
            print(f"[Kijiji] Image {i} has no file_path — skipping.")
            continue
        try:
            print(f"[Kijiji] Downloading image {i}: {file_url[:80]}...")
            resp = requests.get(file_url, timeout=30)
            resp.raise_for_status()
            local_path = os.path.join(product_temp, f"image_{i}.jpg")
            with open(local_path, 'wb') as f:
                f.write(resp.content)
            local_paths.append(local_path)
            print(f"[Kijiji] Saved → {local_path}")
        except Exception as e:
            print(f"[Kijiji] Failed to download image {i}: {e}")

    print(f"[Kijiji] Downloaded {len(local_paths)}/{len(images)} images.")
    return local_paths


def cleanup_temp_images(product_id: str) -> None:
    product_temp = os.path.join(TEMP_FOLDER, product_id)
    try:
        if os.path.exists(product_temp):
            shutil.rmtree(product_temp)
            print(f"[Kijiji] Cleaned up temp folder: {product_temp}")
    except Exception as e:
        print(f"[Kijiji] Cleanup failed: {e}")


# ─── Browser setup ────────────────────────────────────────────────────────────

def get_chrome_version() -> int | None:
    try:
        result = subprocess.run(
            ['reg', 'query', r'HKCU\Software\Google\Chrome\BLBeacon', '/v', 'version'],
            capture_output=True, text=True
        )
        match = re.search(r'(\d+)\.', result.stdout)
        version = int(match.group(1)) if match else None
        print(f"[Kijiji] Detected Chrome version: {version}")
        return version
    except Exception as e:
        print(f"[Kijiji] Could not detect Chrome version: {e} — letting uc pick automatically")
        return None


def setup_browser():
    """Open Chrome using the shared poster profile."""
    import undetected_chromedriver as uc

    print(f"[Kijiji] Browser profile: {CHROME_PROFILE}")
    chrome_version = get_chrome_version()

    opts = uc.ChromeOptions()
    opts.add_argument("--disable-gpu")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--disable-infobars")
    opts.add_argument("--disable-extensions")
    opts.add_argument(f"--user-data-dir={CHROME_PROFILE}")

    browser = uc.Chrome(options=opts, use_subprocess=True, version_main=chrome_version)
    print("[Kijiji] Browser opened.")
    return browser


# ─── Main posting function ────────────────────────────────────────────────────

def post_to_kijiji(product_id: str) -> Dict[str, Any]:
    """Post a product to Kijiji. Returns {"success": bool, ...}."""
    db = get_db()
    product = db.get_product(product_id)

    if not product:
        return {"success": False, "error": "Product not found"}

    if not product.get('title') or not product.get('price'):
        return {"success": False, "error": "Product missing title or price"}

    print(f"\n[Kijiji] ═══ Starting post for: {product.get('title')} ═══")

    # ── Images ──
    image_paths = download_images(product_id)
    if not image_paths:
        return {"success": False, "error": "No images available to upload"}

    browser = None
    try:
        browser = setup_browser()
        print(f"[Kijiji] Navigating to: {POST_URL}")
        browser.get(POST_URL)
        sleep(3)

        # ── Step 1: Title ──────────────────────────────────────────────────────
        print("[Kijiji] Step 1: Entering title...")
        try:
            title_input = WebDriverWait(browser, 15).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="AdTitleForm"]'))
            )
            title = product.get('title', '')[:100]
            if len(title) < 8:           # Kijiji enforces minimum 8 chars
                title = title.ljust(8)
            title_input.send_keys(title)
            print(f"[Kijiji] Title: {title}")
            sleep(1)
        except Exception as e:
            print(f"Failed to fill title: {e}")
            return {"success": False, "error": f"Failed to fill title: {e}"}

        # ── Step 2: Next button ────────────────────────────────────────────────
        print("[Kijiji] Step 2: Clicking Next...")
        # NOTE: if this selector breaks, inspect the button on p-select-category.html
        next_btn = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.XPATH,
                '//*[@id="mainPageContent"]/div/div/div/div[2]/div/div/div[2]/div[1]/div/button'
            ))
        )
        next_btn.click()
        sleep(2)

        # ── Step 3: Category tree — suggested ────────────────────────────────
        print("[Kijiji] Step 3: Selecting Buy & Sell...")
        # NOTE: Kijiji renders category buttons inside #CategorySuggestion.
        # Text match is more robust than positional XPATHs.
        buy_sell = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.XPATH,
                '//*[@id="CategorySuggestion"]/div[1]/ul/li/button'
            ))
        )
        buy_sell.click()
        sleep(2)

        # Wait for the ad form to fully render after category selection
        print("[Kijiji] Waiting for ad form to load...")
        sleep(5)

        # ── Step 6: Upload photos ──────────────────────────────────────────────
        print(f"[Kijiji] Step 6: Uploading {len(image_paths)} images...")
        # NOTE: Kijiji's photo upload may or may not expose a plain file input.
        # If this fails, the old approach was pyautogui on the OS file dialog.
        try:
            file_input = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="file"]'))
            )
            file_input.send_keys("\n".join(image_paths))
            print(f"[Kijiji] Sent {len(image_paths)} paths to file input.")
            sleep(4)
        except Exception as e:
            print(f"[Kijiji] WARNING: File input upload failed: {e}")
            print("[Kijiji] You may need to upload photos manually before clicking Post.")

        # ── Step 7: Condition ──────────────────────────────────────────────────
        print("[Kijiji] Step 7: Setting condition...")
        # NOTE: old selector was By.ID "condition_s" (a <select> element).
        try:
            condition = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.ID, "condition_s"))
            )
            condition.click()
            condition.send_keys(Keys.ARROW_DOWN)
            condition.send_keys(Keys.ENTER)
            print("[Kijiji] Condition set (first option selected).")
            sleep(1)
        except Exception as e:
            print(f"[Kijiji] WARNING: Could not set condition: {e}")
        
        # Fulfillment options
        try:
            cashless_payment = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="payment_s-cashless"]'))
            )
            cash_payment = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="payment_s-cashaccepted"]'))
            )
            cash_payment.click()
            cashless_payment.click()
            print("[Kijiji] Both payment options set (first option selected).")
            sleep(1)
        except Exception as e:
            print(f"[Kijiji] WARNING: Could not set condition: {e}")

        # ── Step 8: Description ────────────────────────────────────────────────
        print("[Kijiji] Step 8: Filling description...")
        # NOTE: old selector was By.ID "pstad-descrptn"
        try:
            desc_input = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.ID, "pstad-descrptn"))
            )
            description = product.get('description', '')
            if description:
                desc_input.send_keys(description[:2000])
                print(f"[Kijiji] Description filled ({len(description)} chars).")
            else:
                print("[Kijiji] No description on product — skipping.")
        except Exception as e:
            print(f"[Kijiji] WARNING: Could not fill description: {e}")

        sleep(1)

        # ── Step 9: Price ──────────────────────────────────────────────────────
        print("[Kijiji] Step 9: Setting price...")
        # NOTE: old selector was By.ID "PriceAmount"
        try:
            price_input = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.ID, "PriceAmount"))
            )
            price = ''.join(filter(str.isdigit, str(product.get('price', '0'))))
            if not price:
                raise ValueError(f"Could not extract numeric price from: {product.get('price')}")
            price_input.send_keys(price)
            print(f"[Kijiji] Price set: {price}")
            sleep(1)
        except Exception as e:
            print(f"[Kijiji] ERROR: Could not set price: {e}")
            return {"success": False, "error": f"Failed to set price: {e}"}

        # ── Step 10: Post ──────────────────────────────────────────────────────
        print("[Kijiji] Step 10: Clicking Post button...")
        # NOTE: old XPATH was positional — using submit button text match instead
        try:
            post_btn = WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable((By.XPATH,
                    '//*[@id="MainForm"]/div[10]/div/div/button'
                ))
            )
            post_btn.click()
            print("[Kijiji] Post button clicked — waiting for confirmation...")
            sleep(6)
        except Exception as e:
            print(f"[Kijiji] ERROR: Could not click Post button: {e}")
            return {"success": False, "error": f"Failed to click Post button: {e}"}

        # ── Update DB ──────────────────────────────────────────────────────────
        print("[Kijiji] Updating product status → posted...")
        db.update_product(
            product_id,
            status="posted",
            posted_at=datetime.utcnow().isoformat()
        )

        cleanup_temp_images(product_id)

        print(f"[Kijiji] ═══ Done: {product.get('title')} ═══\n")
        return {"success": True, "message": "Product posted to Kijiji"}

    except Exception as e:
        print(f"[Kijiji] UNEXPECTED ERROR: {e}")
        traceback.print_exc()
        return {"success": False, "error": str(e)}

    finally:
        if browser:
            sleep(2)
            browser.quit()
            print("[Kijiji] Browser closed.")


# ─── CLI entrypoint ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        result = post_to_kijiji(sys.argv[1])
        print(f"Result: {result}")
    else:
        print("Usage: python kijiji_poster.py <product_id>")
