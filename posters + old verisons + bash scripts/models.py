from dataclasses import dataclass

@dataclass
class ProductData:
    title: str = ""
    price: str = ""
    description: str = ""
    color: str = ""
    brand: str = ""
    tags: str = ""
    link: str = ""