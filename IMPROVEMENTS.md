# Scraper Improvements Log

A running log of bugs found, what led to finding them, and how they were fixed.

---

## 1. Service Startup Script

**File:** `start_all.bat`

**Problem:** Starting the backend, frontend, and Ollama required opening three separate terminals manually every time.

**Fix:** Created `start_all.bat` at the project root that launches all three services in separate Windows Terminal tabs with one double-click:

```bat
wt new-tab --title "Ollama" cmd /k "ollama serve" ;
   new-tab --title "Backend" cmd /k "cd /d ... && uvicorn main:app --reload" ;
   new-tab --title "Frontend" cmd /k "cd /d ... && npm run dev"
```

Uses `%~dp0` so paths are always relative to the script's location regardless of where it's run from.

---

## 2. Image Size Filtering (Pillow)

**File:** `Scraping/base_scraper.py` → `_download_images()`

**Finding:** The scraper was saving everything it found — logos, tracking pixels, tiny thumbnails — because filtering was URL-keyword-based only (checking if "logo" or "icon" appeared in the URL string). Images with generic URLs slipped through.

**Fix:** After downloading each image's bytes, open it with Pillow and check actual pixel dimensions before writing to disk. Reject anything under 300×300:

```python
image = Image.open(io.BytesIO(response.content))
if image.width < 300 or image.height < 300:
    continue
```

This catches small images regardless of what their URL says.

---

## 3. ChromeDriver Version Mismatch

**File:** `Scraping/base_scraper.py` → `_create_driver()`

**Finding:** Error: `"This version of ChromeDriver only supports Chrome version 148, current browser version is 147"`.

Two bugs compounded each other:

1. `webdriver_manager` was downloading ChromeDriver and returning the path, but that path was **never passed** to `uc.Chrome()`. The driver path was fetched into a variable and then ignored:
   ```python
   driver_path = ChromeDriverManager().install()  # downloaded but unused
   driver = uc.Chrome(options=opts)               # uses its own cached driver
   ```

2. `undetected_chromedriver` had a **stale v148 driver cached** locally, which didn't match the installed Chrome 147.

**Fix:** Removed reliance on `webdriver_manager` entirely. Instead, detect the installed Chrome version directly from the Windows registry and pass it to `uc.Chrome` as `version_main`, which forces it to download the correctly matching driver:

```python
def _get_chrome_major_version(self) -> Optional[int]:
    output = subprocess.check_output(
        r'reg query "HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon" /v version', ...
    )
    # parse and return major version int

driver = uc.Chrome(options=opts, version_main=chrome_version, use_subprocess=True)
```

Also required clearing the stale cache: `%USERPROFILE%\.cache\undetected_chromedriver\`

---

## 4. LLM Fallback Was Overwriting Good Data

**File:** `Scraping/base_scraper.py` → `scrape()`

**Finding:** The original LLM fallback called `extract_product_data()` to scrape, then immediately replaced the entire result with `extract_product_data_LLM()` unconditionally — meaning whatever the scraper successfully found was thrown away and rewritten by the LLM every single time:

```python
product = self.extract_product_data()
product = self.extract_product_data_LLM(self.HTML)  # always overwrites
```

**Fix:** Replaced with `_fill_missing_with_llm(product, html)` which checks each field on the `ProductData` object and only asks the LLM to fill in the ones that are empty:

```python
product = self.extract_product_data()
if product:
    product = self._fill_missing_with_llm(product, self.HTML)
```

The LLM receives a template containing only the missing fields, and results are merged back without touching anything the scraper already found.

---

## 5. Wayfair Scraper Bypassed LLM Fallback Entirely

**File:** `Scraping/wayfair_scraper.py` → `scrape()`

**Finding:** The Wayfair scraper overrides `scrape()` from the base class with its own implementation (needed for its aggressive anti-bot bypass logic). Because of this override, the `_fill_missing_with_llm` call added to the base `scrape()` was never reached when scraping Wayfair URLs. Running a Wayfair scrape with a missing price showed no LLM log output at all.

The Wayfair scraper has two exit paths and neither called the LLM:
- **Fast path**: `_extract_from_initial_html()` succeeds → saves and returns immediately
- **Full path**: `extract_product_data()` succeeds → saves and returns immediately

**Fix:** Added `_fill_missing_with_llm` to both exit paths in the Wayfair scraper explicitly.

---

## 6. LLM Response Not Logged / Silent JSON Failures

**File:** `Scraping/base_scraper.py` → `_fill_missing_with_llm()`

**Finding:** When the LLM fallback failed to fill a field, there was no way to know why. The `except` block only printed a one-line error. LLMs frequently wrap JSON in markdown code fences (` ```json ... ``` `) even when instructed not to, causing `json.loads` to crash silently.

**Fix:**
1. Print the raw LLM response to terminal before any parsing
2. Strip markdown code fences before calling `json.loads`
3. Split the exception handler — catch `json.JSONDecodeError` separately and print the raw response alongside it so the cause is always visible

---

## 7. LLM Description Priority

**File:** `Scraping/base_scraper.py` → `_fill_missing_with_llm()`

**Finding:** Scrapers typically extract descriptions from meta tags or short page snippets. These are often truncated marketing blurbs, not full product descriptions. The LLM reading the full page text consistently produces better, more complete descriptions.

**Fix:** `description` is always sent to the LLM regardless of whether the scraper found one. The LLM result and scraper result are compared by character count and the longer one is kept:

```python
if len(llm_description) >= len(scraper_description):
    product.description = llm_description  # LLM wins
else:
    pass  # scraper's version stays
```

---

## 8. Wayfair Images Saving at Low Resolution

**File:** `Scraping/wayfair_scraper.py` → `extract_images()`

**Finding:** Inspecting the live page DOM with Playwright revealed that every product image on Wayfair is served with a `srcset` containing four resolution variants:

```
300w, 600w, 800w, 1200w
```

The scraper was grabbing the `src` attribute, which is always the **800w** version. The 1200w version was sitting unused in the `srcset` on every image.

The old code also tried to upgrade resolution via string replacement (`resize=h800` → `resize=h1200`) but the actual URL pattern was `resize-h800-p1-w800`, so the replacement never matched anything.

Additionally, the thumbnail images in the gallery carousel (64×64 colour swatches, logos, payment icons) only have `1x`/`2x` pixel-density descriptors in their srcset — not `w` width descriptors — which makes them easy to filter out.

**Fix:** Parse the `srcset` attribute for each image, extract all entries with `w` width descriptors, and take the URL with the highest value. Skip any image whose srcset doesn't contain `w` descriptors (thumbnails) or whose best available width is under 600:

```python
def _best_url_from_srcset(self, srcset):
    # parse "url 300w, url 600w, url 1200w" → returns ("url", 1200)

# Only keep images with real width descriptors >= 600px
if not best_url or best_width < 600:
    continue
```

Result: product images now download at 1200×1200 instead of 800×800.
