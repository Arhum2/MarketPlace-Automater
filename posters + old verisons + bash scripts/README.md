
<!-- PROJECT LOGO -->
<br />
<div align="center">
  <h1>Automated Inventory Sourcing, Ad Posting, and Instagram Updates</h1>
  
  ![Flowchart](https://github.com/Arhum2/Manifest-Scrapper/assets/82200170/24995d83-fabc-4056-aa09-5cde9f903417)

  <p align="center">
    <h3>By Arhum Shahzad</h3>
    <br />
    <br />
    <a>
      This project automates manifest processing from Liquidity Services using Python and Selenium, significantly speeding up item lookup for auctions. It has reduced product research and data compilation time from 15 minutes to just 1 minute per manifest. The Auto Ad Poster utilizes this compiled data to swiftly post items on platforms like Facebook and Kijiji, achieving 30 listings in minutes, a task that previously took over two hours manually. The project also features an Instagram Auto Poster that seamlessly updates my business page with current inventory, keeping customers informed about the latest products for sale.

</a>
    <br />
    <br />
    <a href="#step-1-sourcing">View Demo</a>
    ·
    <a href="https://github.com/Arhum2/Manifest-Scrapper/issues">Report Bug</a>
    ·
    <a href="https://github.com/Arhum2/Manifest-Scrapper/pulls">Request Feature</a>
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->
## About The Project
### Here's why I created this project:
* Improved product research and data compiling allowing for less time to be invested with the same return
* You shouldn't be doing the same tasks over and over
* implements DRY principles to my business


## Step 1, Sourcing

Having sourced furniture from [Liquadation.com](https://www.liquidation.com/index?gclid=CjwKCAjwnrjrBRAMEiwAXsCc40uSxzQCMHP_9XwiY_rmfUpJ4WB1EDi4zOMVMNMTv_jmsZp39XRB5xoCpfIQAvD_BwE), I recognized that there was a significant time drain in manual product research of manifests. Using Python and Selenium, I extended and applied this to my business to create the Manifest Scrapper. This tool parses a .CSV file, efficiently searching and retrieving details for each product listed in Liquidity Services manifests. Reducing the processing time per manifest from 15 minutes to just 1 minute.


Here is a full demo of Manifest Scrapper taking in user input (the name of the manifest file) and rapidly looking up each product. 


https://user-images.githubusercontent.com/82200170/187813623-06efb504-6ee3-4f81-b96d-9f58791b8004.mp4 

## Step 2, Positing listings

Prior to implementing this project, the process of gathering data and publishing listings consumed 120 minutes. However, the program's remarkable efficiency has resulted in a staggering 95% reduction in task duration, now requiring a mere 5 minutes and practically no human input.

https://github.com/Arhum2/Manifest-Scrapper/assets/82200170/12002e3e-f338-438d-8569-1919513fc0a8



https://github.com/Arhum2/Manifest-Scrapper/assets/82200170/32907b5b-e31e-4eb4-9310-72ccaaba8122



## Step 3, Instagram updates

Many of my customers wanted to be kept up to date about my inventory, yet the manual task of individually posting each item on Instagram proved to be quite labor-intensive. Thanks to this program, I am now able to uphold a consistent brand presence and effortlessly keep my customers updated on social media regarding new additions to the inventory. 

https://github.com/Arhum2/Manifest-Scrapper/assets/82200170/a1e2a3b4-334c-4dc7-95bd-c77873a0957b



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request <p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- LICENSE -->
### Built With

* [Python](https://www.python.org/)
* [Selenium](https://www.selenium.dev/)
* [PyAutoGUI](https://pyautogui.readthedocs.io/en/latest/#)

### Prerequisites

1. Install [Python](https://www.python.org/)
2. Install [Selenium](https://www.selenium.dev/)
3. Install [Pyautogui](https://pyautogui.readthedocs.io/en/latest/)
4. Check your Chrome version and download your [Chrome driver](https://chromedriver.chromium.org/downloads)

### Installation

1. Clone the repository
   ```sh
   git clone https://github.com/Arhum2/Manifest-Scrapper.git
   ```
2. Change `PATH` in manifest.py to your chromedriver.exe file path
   ```sh
   PATH = 'ENTER chromedriver.exe FILE PATH HERE'
   ```
3. Change line 1 in manifest.bat to your manifest.py file path
   ```js
   @py C:\FILE_PATH\manifest.py %*
   ``` <p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- USAGE EXAMPLES -->

## License

Distributed under the MIT License. See `LICENSE.txt` for more information. <p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTACT -->
## Contact

Email - Arhumshahzad2003@gmail.com <p align="right">(<a href="#readme-top">back to top</a>)</p>
