from WayfairAPI import selenium_extract
from dataclasses import dataclass
from models import ProductData

class BaseParser():
    pass

class WayfairParser(BaseParser):
    def parse(self, url:str):
        product = ProductData()
        selenium_extract(product, url)
        print(product)

if __name__ == "__main__":
    url = "https://www.wayfair.ca/home-improvement/pdp/villar-home-designs-flush-wood-and-pvcvinyl-white-prefinished-flat-double-barn-door-with-installation-double-barn-hardware-kit-vdla1022.html?piid=83654807"
    parser = WayfairParser()
    parser.parse(url)