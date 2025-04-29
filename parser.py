@dataclass
class ProductData:
    title: str
    price: int
    description: str
    color:  str
    brand: str
    tags: str
    link: str

class BaseParser():
    pass

class WayfairParser(BaseParser):
    