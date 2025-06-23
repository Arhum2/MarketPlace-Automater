import os
import re
import time
import requests
import undetected_chromedriver as uc
from AmazonAPI import Amazon_extract, Amazon_extract_images
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

        #create product directory
        product.title = re.sub(r'[<>:\"/\\|?*]', '', product.title)
        self.product_path = os.path.join(self.product_path, product.title)
        if os.path.isdir(self.product_path):
            print("🔻 Error: Product directory already exists")
            return
        os.makedirs(self.product_path, exist_ok=True)
        print(f"✅ Created product directory: {self.product_path}")
        
        #create photos directory
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

    def Amazon_parse_images(self):
        Amazon_extract_images(self)

if __name__ == "__main__":
    #Open and read the file containing URLs
    with open("G:\\My Drive\\selling\\not posted\\links.txt", "r") as file:
        urls = [line.strip() for line in file if line.strip()]
    
    # urls = ["https://www.amazon.com/Y-Decor-NBCL1001-11LED-Ceiling-Brushed-Nickel/dp/B07MC55CDM"]

    for url in urls:
        time.sleep(5)  # Sleep to avoid overwhelming the server
        if "wayfair" in url.lower():
            Wayfair_product = WayfairParser(url)
            product_data = Wayfair_product.parse_data()
            Wayfair_product.parse_images()
            Wayfair_product.write_product_data(product_data)
            Wayfair_product.driver.quit()
        
        if "amazon" in url.lower():
            Amazon_product = AmazonParser(url)
            product_data = Amazon_product.parse_data()
            Amazon_product.Amazon_parse_images()
            Amazon_product.write_product_data(product_data)
            Amazon_product.driver.quit()
        
        else:
            print(f'❌ Unsupported URL: {url}')
    
    print("✅ All products processed successfully.")
