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

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

chrome_service = Service(executable_path="C:\\Program Files (x86)\\chromedriver.exe")

chrome_options = Options()
chrome_options.add_argument('--user-data-dir=C:\\Users\\pokem\\AppData\\Local\\Google\\Chrome\\User Data')
chrome_options.add_argument('--profile-directory=Profile 3')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--remote-debugging-port=9222')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--disable-infobars')

#Navigating to selling folder

os.chdir('G:\\My Drive\\selling\\instagram not posted')
ads = os.listdir()
number_of_adds = len(ads)

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
        self.browser = webdriver.Chrome(service=chrome_service, options=chrome_options)
        self.abs_path = 'G:\\My Drive\\selling\\instagram not posted\\'
        self.post = 'https://www.instagram.com/furniturefrenzy_/'
        self.file_dir = c_file

        #Setting up XPATHs
        self.create_post_btn = '//span[text()="Create"]'
        self.pics_btn = '//button[text()="Select from computer"]'
        self.next_btn = '//div[text()="Next"]'
        self.next_btn2 = '//div[text()="Next"]'
        self.post_btn = '//div[text()="Share"]'
        self.emoji = "//button[@type='button']"
        self.description = '//*[@id="mount_0_0_ms"]/div/div/div[3]/div/div/div[1]/div/div[3]/div/div/div/div/div[2]/div/div/div/div[2]/div[2]/div/div/div/div[2]/div[1]/div[1]'
        self.location = '//*[@id="mount_0_0_OF"]/div/div/div[3]/div/div/div[1]/div/div[3]/div/div/div/div/div[2]/div/div/div/div[2]/div[2]/div/div/div/div[3]/div/label/input'
        self.taglist = "#wayfair #furniture #brampton #toronto #interior #design #decor #ontario #realestatetoronto #interiordesigner #missusagua #jysk #living #rustic #rusticdecor #boho"

    # ==================== Helper Functions ====================

    # Extracts product info from info.txt
    def get_info(self) -> dict:

        x = self.abs_path + self.file_dir.strip('.') + '\\info.txt'
        temp = []
        result = {}

        with open(x, 'r', encoding='utf-8') as txt:
            info = txt.readlines()

            for line in info:
                temp.append(line)

        #{Tags: [list of tags]}
        for line in temp:
            curr_line = line.split(':')
            if curr_line[0] == 'Tags':
                result[curr_line[0]] = None
                x = curr_line[1].split(',')
                for item in x:
                    if result[curr_line[0]] is not None:
                        result[curr_line[0]].append(item.strip())
                    else:
                        result[curr_line[0]] = []
                        result[curr_line[0]].append(item.strip())
            elif ':' in line:
                result[curr_line[0]] = curr_line[1].strip()
            else:
                result['Description'] += curr_line[0].strip()
        
        return result

   # ==================== Automation Function ==================== 
    def automate(self):

        #Navigating to post page and getting info
        self.browser.get(self.post)
        info = self.get_info()

        sleep(2)

        #Filling photo field
        self.create_post_btn = self.browser.find_element(By.XPATH, (self.create_post_btn))
        self.create_post_btn.click()

        sleep(2)

        self.pics_btn = self.browser.find_element(By.XPATH, (self.pics_btn))
        self.pics_btn.click()

        #mutating directory
        photo_directory = self.file_dir.strip('.')
        photo_directory = photo_directory + '\\photo'

        #navigating to photo folder and uploading all photos
        # pyautogui.write(self.abs_path)
        # sleep(2)
        # pyautogui.press('enter')
        sleep(2)
        pyautogui.write('G:\\My Drive\\selling\\instagram not posted')
        sleep(2)
        pyautogui.press('enter')
        sleep(2)
        pyautogui.write(photo_directory)
        sleep(2)
        pyautogui.press('enter')
        sleep(2)
        pyautogui.moveTo(300, 200)
        pyautogui.click()
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.press('enter')
        sleep(2)
        
        self.next_btn = self.browser.find_element(By.XPATH, (self.next_btn))
        self.next_btn.click() 
        sleep(2)
        self.next_btn2 = self.browser.find_element(By.XPATH, (self.next_btn2))
        self.next_btn2.click()

        info = self.get_info()

        pyautogui.moveTo(1600, 450)
        sleep(2)
        pyautogui.click()
        sleep(2)
        pyautogui.write("FOR SALE! " + info['Description'] + '\n' + '\n'+ self.taglist)


        self.post_btn = self.browser.find_element(By.XPATH, (self.post_btn))
        self.post_btn.click()
        
        sleep(2)

        self.browser.quit()




for i in range(number_of_adds):
    curr_file = ads[i]
    testing = f'{os.curdir}\{curr_file}'
    a = Automate_add_post(f'{os.curdir}{curr_file}')
    a.automate()
    sleep(1)
    shutil.move('G:\\My Drive\\selling\\instagram not posted\\' + curr_file, 'G:\\My Drive\\selling\\insta posted\\')
    i += 1


    ### ==== WELCOME TO MY DEMO! ==== ###