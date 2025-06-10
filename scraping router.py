import os
import time
import requests
import undetected_chromedriver as uc
from AmazonAPI import Amazon_extract
from WayfairAPI import selenium_extract, extract_images
from models import ProductData
from fake_useragent import UserAgent


class BaseParser():
    def __init__(self, url=None):
        # --- make a fresh options object every time ---
        opts = uc.ChromeOptions()
        opts.add_argument("--disable-gpu")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--disable-blink-features=AutomationControlled")
        opts.add_argument("--disable-infobars")

        # now build the driver with _this_ new options
        self.driver = uc.Chrome(options=opts)

        self.product_path = "G:\\My Drive\\selling\\not posted\\"
        self.url = url
        self.images = []

    def write_product_data(self, product:ProductData):
        photos_dir = os.path.join(self.product_path, "Photos")
        os.makedirs(photos_dir, exist_ok=True)
        print(f"✅ Created image directory: {photos_dir}") 

        os.chdir(self.product_path)
        f = open("info.txt", "w")
        f.write(f"Title: {product.title}\n")
        f.write(f"Price: {product.price}\n")
        f.write(f"Description: {product.description.strip()}\n")
        f.write(f"Link: {product.link}\n")
        f.close()
        print("✅ Product data written to file")

        for index, image in enumerate(self.images):
            try:
                response = requests.get(image)
                if response.status_code == 200:
                    filename = f'image_{index+1}.jpg'
                    filepath = os.path.join(self.product_path+"\\Photos", filename)
                    with open(filepath, 'wb') as file:
                        file.write(response.content)
                print(f"✅ Saved: {filepath}")
            except Exception as e:
                print(f'❌ Failed to download {image}: {e}')

class WayfairParser(BaseParser):

    def __init__(self, url=None):
        # --- make a fresh options object every time ---
        opts = uc.ChromeOptions()
        opts.add_argument("--disable-gpu")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--disable-blink-features=AutomationControlled")
        opts.add_argument("--disable-infobars")

        # now build the driver with _this_ new options
        self.driver = uc.Chrome(options=opts)

        self.product_path = "G:\\My Drive\\selling\\not posted\\"
        self.url = url
        self.images = []
        #REMOVE THIS, BASE PARSER HAS THE SAME INIT

    def write_product_data(self, product:ProductData):
        photos_dir = os.path.join(self.product_path, "Photos")
        os.makedirs(photos_dir, exist_ok=True)
        print(f"✅ Created image directory: {photos_dir}") 

        os.chdir(self.product_path)
        f = open("info.txt", "w")
        f.write(f"Title: {product.title}\n")
        f.write(f"Price: {product.price}\n")
        f.write(f"Description: {product.description.strip()}\n")
        f.write(f"Link: {product.link}\n")
        f.close()
        print("✅ Product data written to file")

        for index, image in enumerate(self.images):
            try:
                response = requests.get(image)
                if response.status_code == 200:
                    filename = f'image_{index+1}.jpg'
                    filepath = os.path.join(self.product_path+"\\Photos", filename)
                    with open(filepath, 'wb') as file:
                        file.write(response.content)
                print(f"✅ Saved: {filepath}")
            except Exception as e:
                print(f'❌ Failed to download {image}: {e}')

    def parse_data(self):
        product = ProductData()
        scrapped_product = selenium_extract(product, self)
        if scrapped_product:
            print(f"✅ Successfully scraped product data for {product.title}")
            return product
        else:
            print("⚠️ Failed to scrape product data") 
    
    def parse_images(self):
        extract_images(self)
        print("✅ Successfully extracted images")
    
class AmazonParser(BaseParser):
    def __init__(self, url=None):
        # --- make a fresh options object every time ---
        opts = uc.ChromeOptions()
        opts.add_argument("--disable-gpu")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--disable-blink-features=AutomationControlled")
        opts.add_argument("--disable-infobars")
        ua = UserAgent()
        user_agent = ua.random
        opts.add_argument(f'--user-agent={user_agent}')

        # now build the driver with _this_ new options
        self.driver = uc.Chrome(options=opts)
        self.product_path = "G:\\My Drive\\selling\\not posted\\"
        self.url = url
        self.images = []

    def parse_data(self):
        product = ProductData()
        scrapped_product = Amazon_extract(product, self)
        if scrapped_product:
            print(f"✅ Successfully scraped product data for {product.title}")
            return product
        else:
            print("⚠️ Failed to scrape product data") 

    def parse_images(self):
        #TODO 
        pass

if __name__ == "__main__":
    urls = ["https://www.amazon.ca/Coffee-Nightstand-Industrial-Storage-Furniture/dp/B08Y57XHLS?th=1"]
    for url in urls:
        if "wafyair" in url:
            Wayfair_product = WayfairParser(url)
            product_data = Wayfair_product.parse_data()
            Wayfair_product.parse_images()
            Wayfair_product.write_product_data(product_data)
            Wayfair_product.driver.quit()
        
        if "amazon" in url:
            Amazon_product = AmazonParser(url)
            product_data = Amazon_product.parse_data()
