import csv
import sys
import pyperclip
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time

PATH = 'C:\\Program Files (x86)\\chromedriver.exe'

service = webdriver.ChromeService(executable_path=PATH) 
#Service(executable_path=PATH)
browser = webdriver.Chrome(service=service)# check for command line arguments

if len(sys.argv) > 1:
    file_name = ''.join(sys.argv[1:]) + ".csv"
    #print(file_name)

# checking for manifest name on clipboard


else:
    file_name = ''.join(pyperclip.paste()) + ".csv"
    #print(file_name)

# assigning .csv file path

file = f"D:\\download\\{file_name}"

# Read the csv and extract wanted data

with open(f"{file}", 'r') as product_list:
    csv_dict_reader = csv.DictReader(product_list)
    items = []
    for row in csv_dict_reader:
        items.append(row['Product'] + ' ' + row['Manufacturer'])

# While loop to parse the list and google search each product in a new tab

length = len(items)

for item in items:
    browser.get('https://www.google.com/search?q=' + f"{item}")
    browser.switch_to.new_window()

time.sleep(9999)