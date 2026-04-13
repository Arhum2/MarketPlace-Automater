"""
Quick script to see the raw ollama response from extract_product_data_LLM.
1. Put your URL in the URL variable below
2. Run: python test_llm_response.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from ScrapperWebApp.Scraping.base_scraper import BaseScraper

# ---- PUT YOUR URL HERE ----
URL = "https://safavieh.com/rugs/marrakech/mrk749n"
# ---------------------------


class _Scraper(BaseScraper):
    def extract_product_data(self): pass
    def extract_images(self): pass
    def is_supported_url(self, url): pass


scraper = _Scraper(url=URL)

print(f"Launching browser for: {URL}")
scraper.driver = scraper._create_driver()
scraper.driver.get(URL)
html = scraper.driver.page_source
scraper.driver.quit()
print(f"Got {len(html)} characters of HTML\n")

response = scraper.extract_product_data_LLM(html)

print("=== RAW OLLAMA RESPONSE ===")
print(response)
print()
print("=== MESSAGE CONTENT ===")
print(response['message']['content'])
