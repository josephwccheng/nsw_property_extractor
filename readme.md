# Extraction of NSW Property Data

**Date**: 24/04/2023

**Last Updated**: 06/03/2024

**Author**: Joseph Cheng

**Programming Language**: Python3.8 and above

## Disclaimer

- This is a personal, non-profit project that is intended for the public to access datasets, which can potentially help people make decisions when analysing on the property market.
- If the owner / government of this data source requires me to take down this project I will take it down immediately.

## Main Objective

- Property data is difficult to gather through these days. Luckily in New South Wales - Australia, the NSW State Government has provided public dataset of the transactional property sales data (See link below)
- The objective is to create a clean / comprehenable dataset with historical information of the property information in NSW Australia, based on the raw data provided by the government
- Please reach out to me to provide any feedbacks / improvements and I will try my best to update the dataset as soon as possible

## Personal Remarks

- I am also a first home buyer looking for optimisation to find opportunites in the property market. I hope that by sharing this code repository more people can access to property data and help them find their dream home easier.

## How to Run

- Download the data from "NSW data source"
- unzip all the folders and save them in the appropriate location (TODO)
- pip install all the required python library
- run the main file

## Resources

1. [Australian property heat map application](https://heatmaps.com.au/)
2. [NSW Property Sales Information](https://valuation.property.nsw.gov.au/embed/propertySalesInformation)
3. [NSW Bulk Land Value Information](https://www.valuergeneral.nsw.gov.au/land_value_summaries/lv.php)
4. [NSW raw data fields](https://www.valuergeneral.nsw.gov.au/__data/assets/pdf_file/0015/216402/Current_Property_Sales_Data_File_Format_2001_to_Current.pdf)
5. [NSW fields descirption](https://www.valuergeneral.nsw.gov.au/__data/assets/pdf_file/0016/216403/Property_Sales_Data_File_-_Data_Elements_V3.pdf)
6. [Multiprocessing with Python](https://medium.com/geekculture/python-multiprocessing-with-output-to-file-a6748a27ed41)
7. [Python Web Scrapper](https://realpython.com/python-web-scraping-practical-introduction/)
8. [NSW Postcodes](https://www.dva.gov.au/sites/default/files/Providers/nsworp.pdf)
9. [Headers and Cookies for Web Scraping](https://www.scraperapi.com/blog/headers-and-cookies-for-web-scraping/)
10. [Web Scraping best Practices](https://www.scraperapi.com/blog/web-scraping-best-practices/)
11. [10 tips for web scraping](https://www.scraperapi.com/blog/10-tips-for-web-scraping/)

## Anti-scraping Techniques

- number of requests: too many requests within a particular time frame or there are too many parallel requests from the same IP
- number of repetitions and find request patterns (X number of requests at every Y seconds)
- Honeypots are link traps webmasters can add to the HTML file that are hidden from humans
- Redirecting the request to a page with a CAPTCHA
- javascript checks
- anti-bot mechanisms can spot patterns in the number of clicks, clicks’ location, the interval between clicks, and other metrics

## Todos

- Set Your Timeout to at Least 60 seconds
- Don’t Set Custom Headers Unless You 100% Need To
- Always Send Your Requests to the HTTPS Version
- Avoid Using Sessions Unless Completely Necessary
- Manage Your Concurrency Properly
- Verify if You Need Geotargeting Before Running Your Scraper
- If you want to be able to interact with the page (click on a button, scroll, etc.) then you will need to use your own Selenium, Puppeteer, or Nightmare headless browser

## Tips

- Set Random Intervals In Between Your Requests
- Set a Referrer
- Use a Headless Browser
- Avoid Honeypot Traps
- Detect Website Changes
