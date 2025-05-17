import os
import random
import re
from bs4 import BeautifulSoup
import requests
import selenium
headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-CA,en;q=0.9',
    'cache-control': 'max-age=0',
    'cookie': 'FVSID=49-903178fe-d2a0-4cae-9b55-3dea19da498b; WFDC=IAD; i18nPrefs=lang%3Den-CA; CSNUtId=53ae9db0-be9b-4697-b964-c3a9a3764ba3; ExCSNUtId=53ae9db0-be9b-4697-b964-c3a9a3764ba3; vid=23f584c2-66dd-fbb2-80dd-9bfa81143b02; SFSID=7030ee7577607069374d34b6a40a4276; canary=0; serverUAInfo=%7B%22browser%22%3A%22Google%20Chrome%22%2C%22browserVersion%22%3A128%2C%22OS%22%3A%22Windows%22%2C%22OSVersion%22%3A%22%22%2C%22isMobile%22%3Afalse%2C%22isTablet%22%3Afalse%2C%22isTouch%22%3Afalse%7D; CSN_CSRF=a3de6124a5a8882fb53cbf10004d51614313b0033441fb514f2ae1de9c68284a; postalCode=M4C%201B5; pxcts=069fe1c5-6e19-11ef-aaea-235aba82a253; _pxvid=069fd7b5-6e19-11ef-aaea-c6baf8f02a2c; waychatShouldShowChatWindow=false; CSN=g_countryCode%3DCA%26g_zip%3DM4C%25201B5; __ssid=fdfe4133cde97cb34217d63c71a07a7; cjConsent=MHxOfDB8Tnww; cjUser=30d782c7-119f-49b8-877c-f6c1cacc322b; rskxRunCookie=0; rCookie=pm5zjvwhpps7u9zb2hrjt9m0tz07ln; __attentive_id=44b1b7aae55c49e8aa315b9b3d7889ba; _attn_=eyJ1Ijoie1wiY29cIjoxNzI1ODIzOTI1NjMxLFwidW9cIjoxNzI1ODIzOTI1NjMxLFwibWFcIjoyMTkwMCxcImluXCI6ZmFsc2UsXCJ2YWxcIjpcIjQ0YjFiN2FhZTU1YzQ5ZThhYTMxNWI5YjNkNzg4OWJhXCJ9In0=; __attentive_cco=1725823925632; __wid=782462873; _gcl_au=1.1.1101014872.1725823926; __attentive_dv=1; __attentive_ss_referrer=ORGANIC; _gid=GA1.2.844828548.1725823927; _gat_gtag_UA_70989678_1=1; hideGoogleYolo=true; _px3=35e3685a2bd62377e80a4dadf5774a8d582a1492bd44010b1e93cd0f0561f579:Nukbzsqe0WxJVsHhGiRyl11dCLT29oe0gquUVxfuAUB51J/9DvAXZ7O9auzoQ7/908JaVMTuIktpi7x1QGQ6Ig==:1000:0kDgqtwCrOjtkTKy/AW0M9G2dCkdECtN9DibBbiiKu1tPkvXEmLSO8U8AAJOIjDOukmdtYy9XYuicGjRkfdv+V0kqaBr276s0e06sd5iWZ8wYsDsOQKs+tx9ld5ttLzJ/tBiEps7nd/sPGtj0UT/FLH6YAIUg99cmuwre0tPTA/ksPNh5dtPDmGsLnR75OnfunsL0j5FvzTByb+qtEWx/8QzC6Uwmq8qzfgiNRnT6rg=; lastRskxRun=1725823942134; _uetsid=07dda8506e1911efafe4f962c5730d96; _uetvid=07ddac706e1911efab00db843c986920; CSNPersist=page_of_visit%3D7; _ga_G1TPJHGL53=GS1.1.1725823926.1.1.1725823942.44.0.0; __attentive_pv=2; _ga=GA1.2.804046048.1725823926; forterToken=c6ae4329dc2949218824ae42eb6639da_1725823942000__UDF43-m4_20ck_Uvd5PY9QW0Q%3D-13819-v2; forterToken=c6ae4329dc2949218824ae42eb6639da_1725823942000__UDF43-m4_20ck_Uvd5PY9QW0Q%3D-13819-v2; otx=I/WEwmbd+8OA3Zv6gUpEAg==',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
}
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
from models import ProductData
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

options = uc.ChromeOptions()
# options.add_argument(r'--user-data-dir=C:\Users\pokem\AppData\Local\Google\Chrome\User Data')
# options.add_argument(r'--profile-directory=Profile 3')
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--disable-infobars")

product_path = "G:\\My Drive\\selling\\not posted\\"

### HELPERS ###
def mg(soup, prop):
    tag = soup.find("meta", {"property": prop})
    return tag["content"] if tag else None

def expand_all_panels(driver, timeout=10) -> None:
    selectors = [
        (By.CSS_SELECTOR, "#react-collapsed-toggle-\\:R8qml9j7rn7mkq\\:"),
        (By.CSS_SELECTOR, "#react-collapsed-panel-\\:R4qml9j7rn7mkq\\: > div._1dufoctg > button"),
        (By.CSS_SELECTOR, "_1pmvkjd1 _1pmvkjd2 _1pmvkjd6 _1pmvkjd9 _1pmvkjdw"),
        (By.XPATH, "//button[.//p[text()='Specifications']]"),
        # (By.XPATH, "//*[@id=\"react-collapsed-toggle-:Rhiqkmcvesumkq:\"]"),
        (By.XPATH, "//button[.//span[text()[contains(translate(., 'SHOW MORE', 'show more'), 'show more')]]]"),
        # (By.XPATH, "//button[.//span[text()[contains(translate(., 'Specifications', 'specifications'), 'specifications')]]]"),
    ]

    for by, selector in selectors:
        try:
            btn = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((by, selector))
            )
            btn.click()
            print(f'✅ Successfully clicked {selector}')
        except Exception as e:
            print(f"⚠️ Could not click element {selector}")

### SCRAPING ##
def selenium_extract(product, url, driver) -> ProductData:
    print("🌐 Launching browser...")
    driver.get(url)
    print(f"➡️ Navigated to: {url}")
    time.sleep(random.uniform(2, 7))
    expand_all_panels(driver)

# DESCRIPTION
    try:
        selectors = [
            "_1dufoct2",
            "RomanceCopy-text"
        ]

        for selector in selectors:
            try:
                description = driver.find_element(By.CLASS_NAME, selector)
                if description.text:
                    print("✅ Found Description text")
                    product.description = description.text
                    break
            except Exception as e:
                print(f"⚠️ Could not locate element {selector}")

        if not description.text:
            print("⌛ Fallback strategy starting")
            html = driver.page_source
            if soup is None:
                soup = BeautifulSoup(html, "html.parser")
            product.description = mg(soup, "og:description")
             
    except Exception as e:
        print(f"⚠️ Could not locate Romance text")

# TITLE
    try:
        title = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((
                By.CSS_SELECTOR,
                "._6o3atz174.hapmhk7.hapmhkf.hapmhkl"
            ))
        )
        if title:
            print("✅ Found Title text")
            product.title = title.text
    except Exception as e:
            print(f"⚠️ Could not locate Title text")

    if not title.text:
        print("⌛ Fallback strategy starting")
        if soup is None:
            soup = BeautifulSoup(html, "html.parser")
        product.title = mg(soup, "og:title")
        product.title = re.sub(r'[<>:"/\\|?*]', '', product.title)

# Price 
    try:
        price = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((
                By.CSS_SELECTOR,
                "._6o3atzbl._6o3atzc7._6o3atz19j"
            ))
        )
        if price:
            print("✅ Found Price text")
            product.price = price.text

    except Exception as e:
            print(f"⚠️ Could not locate Title text")

# Link
    product.link = url

# Create product folder
    product_path = product_path + product.title
    
    if os.path.isdir(product_path):
        print("🔻 Error: Product directory already exists")
        return
    
    os.makedirs(product_path, exist_ok=True)

# call extract images
    extract_images(driver, soup, url)
    driver.quit()
    return product

def extract_images(driver=None, soup=None, url=str):    
    if driver is None:
        driver = uc.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        driver.get(url)

    time.sleep(5)  # Wait for JS to load images

    if soup is None:
        soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    images = soup.find_all("img")
    
    image_path = product_path + "\\photos"
    if os.path.isdir(image_path):
        print("🔻 Error: Photo directory already exists")
        return
    
    os.makedirs(image_path, exist_ok=True)

    for index, url in enumerate(images):
        src = url.get('src') or url.get('data-src')
        if src and 'h800' in src:
            try:
                response = requests.get(src)
                if response.status_code == 200:
                    filename = f'image_{index+1}.jpg'
                    filepath = os.path.join(image_path, filename)

                    with open(filepath, 'wb') as file:
                        file.write(response.content)
                print(f"✅ Saved: {filepath}")
            except Exception as e:
                print(f'❌ Failed to download {src}: {e}')
    driver.quit()

# === Debuging code === #
# product = ProductData()
# #remove later, driver object should come from router
# options = uc.ChromeOptions()
# options.add_argument("--disable-gpu")
# options.add_argument("--no-sandbox")
# options.add_argument("--disable-dev-shm-usage")
# options.add_argument("--disable-blink-features=AutomationControlled")
# options.add_argument("--disable-infobars")
# driver = uc.Chrome(options=options)

# selenium_extract(product=product, url="https://www.wayfair.ca/home-improvement/pdp/villar-home-designs-flush-wood-and-pvcvinyl-white-prefinished-flat-double-barn-door-with-installation-double-barn-hardware-kit-vdla1022.html?piid=83654807",driver=driver)