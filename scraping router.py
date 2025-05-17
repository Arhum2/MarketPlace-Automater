import os
import time
import undetected_chromedriver as uc
from WayfairAPI import selenium_extract, extract_images
from dataclasses import dataclass
from models import ProductData
product_path = "G:\\My Drive\\selling\\not posted\\"
options = uc.ChromeOptions()
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--disable-infobars")


class BaseParser():
    pass

class WayfairParser(BaseParser):

    def __init__(self):
        self.driver = uc.Chrome(options=options)

    def write_product_data(self, product:ProductData):
        product_path = product_path + product.title

        if os.path.isdir(product_path):
            print("🔻 Error: Product directory already exists")
            print("🔻 Deleting existing directory...")
            os.rmdir(product_path)

        os.makedirs(product_path, exist_ok=True)
        os.chdir(product_path + "\\")
        f = open("info.txt", "w")
        f.write(f"Title: {product.title}\n")
        f.write(f"Price: {product.price}\n")
        f.write(f"Description: {product.description}\n")
        f.write(f"Link: {product.link}\n")
        f.close()
        print("✅ Product data written to file")        


    def parse_data(self, url:str):
        product = ProductData()
        scrapped_product = selenium_extract(product, url, driver=self.driver)
        if scrapped_product:
            print(f"✅ Successfully scraped product data for {product.title}")
            return product
        else:
            print("⚠️ Failed to scrape product data") 
    
    def parse_images(self, product:ProductData):
        extract_images(driver=self.driver, url=product.link)
        print("✅ Successfully extracted images")

        
if __name__ == "__main__":
    url = "https://www.wayfair.ca/home-improvement/pdp/villar-home-designs-flush-wood-and-pvcvinyl-white-prefinished-flat-double-barn-door-with-installation-double-barn-hardware-kit-vdla1022.html?piid=83654807"
    current_item = ProductData()  
    if "wayfair" in url:

        parser = WayfairParser()
        product_data = parser.parse_data(url)
        parser.write_product_data(product_data)
        parser.parse_images(product_data)