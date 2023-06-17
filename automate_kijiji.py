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

os.chdir('G:\\My Drive\\selling\\not posted')
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
        self.abs_path = 'G:\\My Drive\\selling\\not posted\\'
        self.post = 'https://www.kijiji.ca/p-select-category.html'
        self.file_dir = c_file

        #Setting up XPATHs
        self.ad_title = '//*[@id="AdTitleForm"]'
        self.ad_next_btn = '//*[@id="mainPageContent"]/div/div/div/div[2]/div/div/div[2]/div[1]/div/button'
        self.buy_n_sell_btn = '//*[@id="CategorySuggestion"]/div/ul/li[1]/button/span'
        self.furniture_btn = '//*[@id="CategorySuggestion"]/div/ul[2]/li[14]/button/span'
        self.other_btn = '//*[@id="CategorySuggestion"]/div/ul[2]/li[13]/button/span'
        self.dropoff_btn = '//*[@id="MainForm"]/div[3]/div/section/div[2]/div[4]/fieldset/div/div/div[1]/label'
        self.curbside_btn = '//*[@id="MainForm"]/div[3]/div/section/div[2]/div[4]/fieldset/div/div/div[3]/label'
        self.cashless_btn = '//*[@id="MainForm"]/div[3]/div/section/div[2]/div[5]/fieldset/div/div/div[1]/label'
        self.cash_btn = '//*[@id="MainForm"]/div[3]/div/section/div[2]/div[5]/fieldset/div/div/div[2]/label'
        self.condition_drop = '//*[@id="condition_s"]'


    # ==================== Helper Functions ====================

    # Extracts product info from info.txt
    def get_info(self) -> dict:

        x = self.abs_path + self.file_dir.strip('.') + '\\info.txt'
        temp = []
        result = {}

        with open(x, 'r') as txt:
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
            else:
                result[curr_line[0]] = curr_line[1].strip()
        
        return result

   # ==================== Automation Function ==================== 
    def automate(self):

        #Navigating to post page and getting info
        self.browser.get(self.post)
        info = self.get_info()

        #Filling photo field
        self.ad_title = self.browser.find_element(By.XPATH, (self.ad_title))

        if len(info['Title']) < 8:
            x = 8 - len(info['Title'])
            self.ad_title.send_keys(info['Title']+ ' ' * x)
        else:
            self.ad_title.send_keys(info['Title'])

        self.ad_next_btn = self.browser.find_element(By.XPATH, (self.ad_next_btn))
        self.ad_next_btn.click()

        sleep(2)
        
        self.buy_n_sell_btn = self.browser.find_element(By.XPATH, (self.buy_n_sell_btn))
        self.buy_n_sell_btn.click()

        sleep(2)

        self.furniture_btn = self.browser.find_element(By.XPATH, (self.furniture_btn))
        self.furniture_btn.click()

        sleep(2)

        self.other_btn = self.browser.find_element(By.XPATH, (self.other_btn))
        self.other_btn.click()

        sleep(4)

        self.dropoff_btn = self.browser.find_element(By.XPATH, (self.dropoff_btn))
        self.dropoff_btn.click()
        self.curbside_btn = self.browser.find_element(By.XPATH, (self.curbside_btn))
        self.curbside_btn.click()
        self.cashless_btn = self.browser.find_element(By.XPATH, (self.cashless_btn))
        self.cashless_btn.click()
        self.cash_btn = self.browser.find_element(By.XPATH, (self.cash_btn))
        self.cash_btn.click()

        self.condition_drop = self.browser.find_element(By.XPATH, (self.condition_drop))
        self.condition_drop.click()
        self.condition_drop.send_keys(Keys.ARROW_DOWN)
        self.condition_drop.send_keys(Keys.ENTER)



        x = 2 + 2






        try:
            try:
                self.title_button = self.browser.find_element(By.XPATH, (self.title_button))
                self.title_button.send_keys(info['Title'])
                gate = True
        
            except NoSuchElementException:
                self.title_button = self.browser.find_element(By.XPATH, (self.title_button2))
                self.title_button.send_keys(info['Title'])
                gate = True
        
        except NoSuchElementException:
            self.title_button = self.browser.find_element(By.XPATH, (self.title_button3))
            self.title_button.send_keys(info['Title'])

            

        try:
            self.price_button = self.browser.find_element(By.XPATH, (self.price_button))
            self.price_button.send_keys(info['Price'])
        
        except NoSuchElementException:
            self.price_button = self.browser.find_element(By.XPATH, (self.price_button2))
            self.price_button.send_keys(info['Price'])

        #Drop down properties
        try:
            self.category_drop = self.browser.find_element(By.XPATH, self.category_drop).click() #reassigning selfs vars to the found element, probably not gonna be used again but good to have
            self.category_furniture = self.browser.find_element(By.XPATH, self.category_furniture).click()
        
        except NoSuchElementException:
            self.category_drop = self.browser.find_element(By.XPATH, self.category_drop2).click()
            self.category_furniture = self.browser.find_element(By.XPATH, self.category_furniture).click()

        try:
            self.condition_drop = self.browser.find_element(By.XPATH, self.condition_drop).click()
            try:
                self.condition_new = self.browser.find_element(By.XPATH, self.condition_new).click()
            except:
                self.condition_new = self.browser.find_element(By.XPATH, self.condition_new2).click()
        except:
            self.condition_drop = self.browser.find_element(By.XPATH, self.condition_drop2).click()
            try:
                self.condition_new = self.browser.find_element(By.XPATH, self.condition_new).click()
            except:
                self.condition_new = self.browser.find_element(By.XPATH, self.condition_new2).click()
                
        try:
            try:
                self.brand = self.browser.find_element(By.XPATH, self.brand)
                self.brand.send_keys(info['Brand'])
            except:
                try:
                    self.brand = self.browser.find_element(By.XPATH, self.brand2)
                    self.brand.send_keys(info['Brand'])
                
                except NoSuchElementException:
                    pass
        
        except:
            pass

        if info['Color']: #Bandaid fix
            try:
                try:
                    self.color = self.browser.find_element(By.XPATH, (self.color))
                    self.color.send_keys(info['Color'])
                
                except:
                    self.color = self.browser.find_element(By.XPATH, (self.color2))
                    self.color.send_keys(info['Color'])
            
            except NoSuchElementException:
                pass

        try:
            self.description = self.browser.find_element(By.XPATH, (self.description))
            self.description.click()
            self.description.send_keys(info['Description'])
        
        except ElementNotInteractableException: 
            self.description = self.browser.find_element(By.XPATH, (self.description2))
            self.description.click()
            self.description.send_keys(info['Description'])

        try:
            self.tags = self.browser.find_element(By.XPATH, (self.tags))
        
        except NoSuchElementException:
            self.tags = self.browser.find_element(By.XPATH, (self.tags2))

        for tag in info['Tags']:
            self.tags.send_keys(tag)
            self.tags.send_keys(Keys.ENTER)

        self.done = self.browser.find_element(By.XPATH, (self.done))
        self.done.click()

        self.browser.close()



for i in range(number_of_adds):
    curr_file = ads[i]
    testing = f'{os.curdir}\{curr_file}'
    a = Automate_add_post(f'{os.curdir}{curr_file}')
    a.automate()
    sleep(10)
    i += 1