import asyncio
import re
import requests
from PIL import Image
from io import BytesIO
from bs4 import BeautifulSoup
import pyperclip
import sys
import os
import json
from DeeperSeek import DeepSeek
import dotenv
dotenv.load_dotenv()

DEEP_SEEK_EMAIL = os.getenv("DEEP_SEEK_EMAIL")
DEEP_SEEK_PASSWORD = os.getenv("DEEP_SEEK_PASSWORD")
DEEP_SEEK_TOKEN = os.getenv("DEEP_SEEK_TOKEN")
link = "https://www.wayfair.ca/outdoor/pdp/bay-isle-home-tuskegee-5-piece-sofa-seating-group-with-cushions-c011241229.html"


async def main():

# ==== LINK EXTRACTION ====
    # if len(sys.argv) > 1:
    #     link = ''.join(sys.argv[1:])
    # else:
    #     link = ''.join(pyperclip.paste())    

# ==== WEB SCRAPING ====
    api = DeepSeek(
        email= DEEP_SEEK_EMAIL,
        password = DEEP_SEEK_PASSWORD,
        token = DEEP_SEEK_TOKEN,
        chat_id=None,
        chrome_args=None,
        verbose=False,
        headless=False,
        attempt_cf_bypass=True,
    )

# ==== Starting DeepSeek query ====
    await api.initialize() 
    await api.switch_chat("f52e3425-f095-4ec5-aaa1-232ba5949bf4") # Switch to the chat with the specified chat ID

    response = await api.send_message(
    # "I've extracted the HTML code for a furniture product page. Extract important information from the HTML code such as the product name, price, and description. The extracted information should be returned in a dictionary format, do not return anything else besides this dictionary format. Here is the HTML code: \n\n" + cleaned_text, # The message to send
    f"......Here is a link to a wayfair product page, do the same for this link as you did with the others: {link}", # The message to send
    deepthink = False, 
    search = True, # Whether to use the Search option or not
    slow_mode = True, # Whether to send the message in slow mode or not
    slow_mode_delay = 0.1, # The delay between each character when sending the message in slow mode
    timeout = 300, # The time to wait for the response before timing out
    ) 


# ==== FILE NAVIGATING AND WRITING ====
    # f = open('/Users/arhumshahzad/Library/CloudStorage/GoogleDrive-arhumshahzad2003@gmail.com/My Drive/selling/not posted/text.txt', 'r')
    # content = f.read()
    # f.close()
    extract_info(response.text)

def extract_info(content):
    cleaned = []
    lines = content.split("\n")
    for line in lines:
        line = line.strip()
        if ("(Due to technical issues, the search service is temporarily unavailable.)" in line or line == ""):
            continue
        cleaned.append(line)
    
    # mac_path = "/Users/arhumshahzad/Library/CloudStorage/GoogleDrive-arhumshahzad2003@gmail.com/My Drive/selling/not posted/"
    windows_path = "G:\\My Drive\\selling\\not posted\\"
    
    #Error case either server failed or response format is wrong
    if cleaned == []:
        rePrompt(link)
    product_name = cleaned[0].split(":")[1].strip()
    product_path = windows_path + product_name
    
    os.makedirs(product_path, exist_ok=True)
    os.chdir(product_path + "\\")
    f = open("info.txt", 'x')

    for line in cleaned:
        f.write(line + "\n")
    f.close()
    
# ==== HELPERS ====
async def rePrompt(link):
    api = DeepSeek(
        email = DEEP_SEEK_EMAIL,
        password = DEEP_SEEK_PASSWORD,
        token = DEEP_SEEK_TOKEN,
        chat_id = None,
        chrome_args = None,
        verbose = False,
        headless = False,
        attempt_cf_bypass = True,
    )
    
    await api.initialize()

    response = await api.send_message(
        f"""
        Here is the link {link}, follow these instructions to extract the information from the link, also make sure to add a newline character at the end of each category (i.e after Tittle is done, add a newline character before starting Price).: 
        instructions for DeepSeek Instance:

        Response Format: Always structure responses in the following format:

        Title: [Product Name]

        Price: [Price]

        Description: [Brief, engaging description of the product, highlighting key features and benefits]

        Technical Details: [Concise list of technical specifications, separated by periods, no bullet points]

        Color: [Color options, if applicable]

        Brand: [Brand name]

        Tags: [Relevant tags separated by commas, focusing on product type, style, and use cases]

        Link: [Full product URL]

        Tone and Style:

        Use clear, concise, and engaging language.

        Avoid unnecessary fluff or repetition.

        Ensure the description is informative but not overly technical.

        Technical Notes:

        If technical details are available, include them in a single paragraph, separated by periods.

        Do not use bullet points or numbered lists.

        Consistency:

        Always follow the exact format provided above.

        Do not deviate from the structure unless explicitly instructed.

        Example Template:

        Copy
        **Title**: [Product Name]  
        **Price**: [Price]  
        **Description**: [Description]  
        **Technical Details**: [Technical details]  
        **Color**: [Color]  
        **Brand**: [Brand]  
        **Tags**: [Tags]  
        **Link**: [Link]  
        """
    )

    extract_info(response.text)
    
# Run the asynchronous main function
if __name__ == "__main__":
    asyncio.run(main())

