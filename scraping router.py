import os
import time
import requests
import undetected_chromedriver as uc
from WayfairAPI import selenium_extract, extract_images
from dataclasses import dataclass
from models import ProductData
options = uc.ChromeOptions()
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--disable-infobars")

class BaseParser():
    pass

class WayfairParser(BaseParser):

    def __init__(self, url:str):
        self.driver = uc.Chrome(options=options)
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
        
if __name__ == "__main__":
    url = "https://www.wayfair.ca/furniture/pdp/union-rustic-kira-solid-wood-platform-bed-c001463350.html?piid=1018097458%2C994815929"
    current_item = ProductData()  
    if "wayfair" in url:

        Wayfair_product = WayfairParser(url)
        product_data = Wayfair_product.parse_data()
        Wayfair_product.parse_images()
        Wayfair_product.write_product_data(product_data)
