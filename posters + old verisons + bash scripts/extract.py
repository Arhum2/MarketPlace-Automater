import asyncio
import json
import re
import sys
import time
import requests
from bs4 import BeautifulSoup
import os
import os, openai
import dotenv
dotenv.load_dotenv()
from bs4 import BeautifulSoup
from config import *
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from DeeperSeek import DeepSeek
from selenium.webdriver import ActionChains
from DeeperSeek.internal.exceptions import ServerDown

DEEP_SEEK_EMAIL = os.getenv("DEEP_SEEK_EMAIL")
DEEP_SEEK_PASSWORD = os.getenv("DEEP_SEEK_PASSWORD")
DEEP_SEEK_TOKEN = os.getenv("DEEP_SEEK_TOKEN")
product_path = 'G:\\My Drive\\selling\\not posted' #making global var, assigned in extract_info() 
openai.api_key = os.getenv('OPENAI_KEY')

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

def extract_images(url):    
    options = uc.ChromeOptions()
    options.add_argument('--user-data-dir=C:\\Users\\pokem\\AppData\\Local\\Google\\Chrome\\User Data')
    options.add_argument('--profile-directory=Profile 3')
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-infobars")

    driver = uc.Chrome(options=options, use_subprocess=True)

    driver.get(url)

    time.sleep(5)  # Wait for JS to load images

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    images = soup.find_all('img')

    images = soup.find_all("img")
    image_path = product_path + "\\photos"
    if os.path.isdir(image_path):
        return
    else:
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

def expand_all_panels(driver):
    selectors = [
        "#react-collapsed-toggle-\:R8qml9j7rn7mkq\:",
        "#react-collapsed-panel-\:R4qml9j7rn7mkq\: > div._1dufoctg > button"
    ]

    for selector in selectors:
        try:
            element = driver.find_element(By.CSS_SELECTOR, selector)
            element.click()
        except Exception as e:
            print(f"⚠️ Could not click element {selector}")

def extract_source_code(url):
    options = uc.ChromeOptions()
    options.add_argument(r'--user-data-dir=C:\Users\pokem\AppData\Local\Google\Chrome\User Data')
    options.add_argument(r'--profile-directory=Profile 3')
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-infobars")

    driver = uc.Chrome(options=options)

    try:
        driver.get(url)
        time.sleep(5)
        try:
            expand_all_panels(driver)
        except:
            pass
        html = driver.page_source
    finally:
        driver.quit()
    
    return html

def extract_info_soup(url, html):

    soup = BeautifulSoup(html, "html.parser")    
     
    def mg(prop):
        tag = soup.find("meta", {"property": prop})
        return tag["content"] if tag else None
    
    snippet = {
        "title":       mg("og:title"),
        "description": mg("og:description"),
        "link":        url
    }

    with open("G:\\My Drive\\selling\\not posted\\test scrap folder\\details.txt", "w", encoding="utf-8") as f:
        f.write(str(snippet))

async def extract_info_DeepSeek(url):
    """
    Returns True if DeepSeek extracted & wrote the info successfully,
    or False on any error (network, timeout, parse, filesystem…).
    """
    api = DeepSeek(
        token=DEEP_SEEK_TOKEN,
        email=DEEP_SEEK_EMAIL,
        password=DEEP_SEEK_PASSWORD,
        headless=True,
        attempt_cf_bypass=True,
        verbose=True
    )

    try:
        await api.initialize()
        await api.switch_chat("f52e3425-f095-4ec5-aaa1-232ba5949bf4")
        response = await api.send_message(
            f"Parse product page: {url}",
            deepthink=False,
            search=True,
            slow_mode=True,
            timeout=300,
        )
    except ServerDown as e:
        print(f"⚠️ DeepSeek server busy, skipping: {e}")
        return False
    except Exception as e:
        print(f"⚠️ [DeepSeek API error] {e}")
        return False

    content = response.text
    
    match = re.search(r'(\{.*\})', content, flags=re.DOTALL)
    if not match:
        print(f"⚠️ [DeepSeek no JSON] got:\n{content}\n")
        raise ValueError("No JSON object found")

    json_str = match.group(1)

    data = json.loads(json_str)

    windows_path = "G:\\My Drive\\selling\\not posted\\"
    
    product_name = re.sub(r'[<>:"/\\|?*]', '', data["Title"])
    product_name = product_name.encode('ascii', 'ignore').decode('ascii')
    product_path = windows_path + product_name
    
    if os.path.isdir(product_path):
        print("⚠ ERROR: Product directory already exists")
        return
    
    os.makedirs(product_path, exist_ok=True)
    os.chdir(product_path + "\\")
    f = open("info.txt", 'x')
    for key in data:
        f.write(f'{key}: {data[key]}\n')
    f.close()

async def extract_info_DeepSeek_Reprompt(html):
    # ==== WEB SCRAPING ====
    api = DeepSeek(
        token = DEEP_SEEK_TOKEN,
        email=DEEP_SEEK_EMAIL,
        password=DEEP_SEEK_PASSWORD,
        headless=False,
        attempt_cf_bypass=True,
        verbose=True
    )

    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "noscript", "iframe", "link", "footer", "nav", "aside"]):
        tag.decompose()
    for el in soup.find_all():
        el.attrs = {}
    clean_html = str(soup)
    clean_html = re.sub(r"\s+", " ", clean_html).strip()
    clean_html.replace("<", "")
    clean_html.replace(">", "")
    clean_html.replace("div", "")
    clean_html.replace("//", "")
    

# ==== Starting DeepSeek query ==== 
    await api.initialize() 

    response = await api.send_message(
    # "I've extracted the HTML code for a furniture product page. Extract important information from the HTML code such as the product name, price, and description. The extracted information should be returned in a dictionary format, do not return anything else besides this dictionary format. Here is the HTML code: \n\n" + cleaned_text, # The message to send
    f"......Here is the source code to a site with a furniture product, take the code and extract all its information in a JSON format containing Title, Description, Price, and the Link to the product. Here is the source code {clean_html}", # The message to send
    deepthink = False, 
    search = True, # Whether to use the Search option or not
    slow_mode = True, # Whether to send the message in slow mode or not
    timeout = 300, # The time to wait for the response before timing out
    ) 

    content = response.text
    
    match = re.search(r'(\{.*\})', content, flags=re.DOTALL)
    if not match:
        print("⚠ ERROR, DEEPSEEK RESPONSE: ", content)
        raise ValueError("No JSON object found")

    json_str = match.group(1)

    data = json.loads(json_str)

    windows_path = "G:\\My Drive\\selling\\not posted\\"
    
    product_name = re.sub(r'[<>:"/\\|?*]', '', data["Title"])
    product_name = product_name.encode('ascii', 'ignore').decode('ascii')
    product_path = windows_path + product_name
    
    if os.path.isdir(product_path):
        print("⚠ ERROR: Product directory already exists")
        return
    
    os.makedirs(product_path, exist_ok=True)
    os.chdir(product_path + "\\")
    f = open("info.txt", 'x')
    for key in data:
        f.write(f'{key}: {data[key]}\n')
    f.close()


# Run the asynchronous main function
if __name__ == "__main__":
    if len(sys.argv) >= 2:
        pass
    else:

        if True:
            f = open("G:\\My Drive\\selling\\not posted\\links.txt", "r")
            lines = f.readlines()
            for index, link in enumerate(lines):
                print(f"\n🔗 Processing link #{index}\n")
                try:
                    asyncio.run(extract_info_DeepSeek(link))
                except Exception as e:
                    print(f"⚠️ DeepSeek failed: {e}")
                
                    #Fallback
                    try:
                        html = extract_source_code(link)
                        asyncio.run(extract_info_DeepSeek_Reprompt(html))
                    except Exception as e2:
                        print(f'!! extract_info_soup also failed: {e2}')
                try:
                    extract_images(link)
                except Exception as e:
                    print(f"❌ extract_images failed: {e3}")
