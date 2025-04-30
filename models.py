from dataclasses import dataclass

@dataclass
class ProductData:
    title: str = ""
    price: int = 0
    description: str = ""
    color: str = ""
    brand: str = ""
    tags: str = ""
    link: str = ""