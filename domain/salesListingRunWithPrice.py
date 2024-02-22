from domainAdaptor import SalesFilter
from domainSalesListing import SalesListing
from datetime import date
import time
import random
from tqdm import tqdm

from fileProcessing import createEmptyCsvWithHeaders, appendRowsToCsv

baseURL = 'https://www.domain.com.au/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/118.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br'
}

pricing = {"0-300000": "min", "300001-1000000": "50000", "1000001-3000000": "100000",
           "3000001-5000000": "250000", "5000001-12000000": "500000", "12000000-any": "max"}
if __name__ == "__main__":
    # examples, chatswood, st leonards, willoughby
    inputSuburb = input("Enter a NSW Suburb (Spelling is critical): ")
    fileName = f'{inputSuburb.lower().replace(" ", "_")}_sales_list_{date.today()}.csv'
    salesListing = SalesListing(baseURL, headers)
    rawSalesListingResp = salesListing.getSalesListingBySuburb(inputSuburb)
    salesData = salesListing.extractRawSalesData(
        rawSalesListingResp)
    salesSummaryData = salesData["salesSummaryData"]
    saleList = salesData["salesList"]

    createEmptyCsvWithHeaders(fileName, saleList[0].keys())
    appendRowsToCsv(fileName, saleList[0].keys(), saleList)
    # Loop through all pagination & obtain all sales property listing
    for page in tqdm(range(2, salesSummaryData["totalPages"] + 1)):
        rawSalesListingResp = salesListing.getSalesListingBySuburb(
            inputSuburb, SalesFilter(price=""), page)
        saleList = salesListing.extractRawSalesData(
            rawSalesListingResp)['salesList']
        appendRowsToCsv(fileName, saleList[0].keys(), saleList)
        # performing a sleeper just so we dont spam domain and get banned
        time.sleep(random.randint(1, 3))

    print(f"completed with sales summary data: {salesSummaryData}")
