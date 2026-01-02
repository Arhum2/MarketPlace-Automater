import selenium.webdriver as webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import os
from time import sleep
import pyautogui
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotInteractableException
import shutil
from config import *
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

#make chrome service using package that downloads the latest chromedriver
chrome_driver_path = "C:\\Program Files (x86)\\chromedriver.exe"
service = Service(executable_path=chrome_driver_path)


opts = Options()
opts.add_argument("--disable-gpu")
opts.add_argument("--disable-blink-features=AutomationControlled")
opts.add_argument("--disable-infobars")
opts.add_argument("--disable-extensions")
opts.add_argument('--user-data-dir=C:\\ChromeProfiles\\FBProfile')
opts.add_experimental_option("excludeSwitches", ["enable-automation"])
opts.add_experimental_option("useAutomationExtension", False)


#Navigating to selling folder
os.chdir(SELLING_FOLDER)
ads = os.listdir(SELLING_FOLDER)
number_of_adds = len(ads)
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

# browser = webdriver.Chrome(service=chrome_service, options=chrome_options)

#Automate class and script
class Automate_add_post:
    """
    browser: chrome browser
    post: facebook add post screen
    photo button: add photos button
    """

    def __init__(self, c_file,) -> None:

        #Setting up browser, File paths, etc
        self.browser = webdriver.Chrome(service=service, options=opts)
        sleep(2)
        self.abs_path = NOT_POSTED_FOLDER
        self.post = 'https://www.facebook.com/marketplace/create/item'
        self.file_dir = c_file
        self.photo_button = "//span[text()='Add Photos']"
        
        self.done = '//span[text()="Save draft"]'


    # extracting info from info.txt
    def get_info(self) -> dict:

        x = self.abs_path + self.file_dir.strip('.') + '\\info.txt'
        result = {}
        keys = ["title", "price", "description", "link"]

        with open(x, 'r', encoding='utf-8', errors="replace") as txt:
            lines = txt.readlines()
                
        key = None
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if ":" in line and line.split(":", 1)[0].isalpha() and line.split(":", 1)[0].lower() in keys:
                key, value = line.split(":", 1)
                result[key.strip()] = value.strip()
            elif key:
                result[key.strip()] += ' ' + line.strip()
        
        return result
    
    def automate(self):
        self.browser.get(self.post)
        sleep(3)

    #Filling text fields
        info = self.get_info()

    # === TITLE ===
        pyautogui.moveTo(50, 700)
        pyautogui.click()
        pyautogui.write(info['Title'])
        sleep(2)

    # === PRICE ===
        pyautogui.moveTo(50, 810)
        pyautogui.click()
        pyautogui.write(info['Price'])
        sleep(2)

    # === CATEGORY & CONDITION ===
        pyautogui.moveTo(50, 900)
        pyautogui.click()
        sleep(2)
        pyautogui.moveTo(50, 1050)
        sleep(2)
        pyautogui.click()
        pyautogui.moveTo(50, 1000)
        sleep(2)
        pyautogui.click()
        sleep(2)
        pyautogui.moveTo(50, 1030)
        pyautogui.click()
        sleep(2)
      
    # === DESCRIPTION ===
        pyautogui.moveTo(50, 1100)
        pyautogui.click()
        pyautogui.write(info['Description'])
        pyautogui.press('enter')
        pyautogui.write(info['Link'])

        sleep(15)

        # === PHOTOS ===
        photo_directory = self.file_dir.strip('.')
        photo_directory = photo_directory + '\\Photos'               
        #Filling photo field
        try:
            self.photo_button = self.browser.find_element(By.XPATH, (self.photo_button))
            self.photo_button.click()        

        except:
            pyautogui.moveTo(120, 300)
            sleep(2)
            pyautogui.click()
                
                
        #
        # navigating to photo folder and uploading all photos
        # pyautogui.write(self.abs_path)
        # sleep(2)
        # pyautogui.press('enter')
        sleep(2)
        pyautogui.write('G:\\My Drive\\selling\\not posted\\' + photo_directory)
        sleep(2)
        pyautogui.press('enter')
        sleep(2)
        # pyautogui.write(photo_directory)
        # sleep(2)
        # pyautogui.press('enter')
        sleep(2)
        pyautogui.moveTo(300, 200)
        pyautogui.click()
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.press('enter')
        sleep(2)
            

        sleep(7)
        self.done = self.browser.find_element(By.XPATH, (self.done))
        self.done.click()

        self.browser.close()



for i in range(number_of_adds):
    curr_file = ads[i]
    a = Automate_add_post(f'{os.curdir}{curr_file}')
    a.automate()
    print(f'✅ POSTED {curr_file}')
    sleep(1)
    shutil.move('G:\\My Drive\\selling\\not posted\\' + curr_file, 'G:\\My Drive\\selling\\instagram not posted\\')
    i += 1

print("TASK COMPLETED")