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


def getSalesDataAndSaveToCSV(inputSuburb: str, priceIndex: int, fileName: str, fileCreated: bool, page: int):
    rawSalesListingResp = salesListing.getSalesListingBySuburb(
        inputSuburb, SalesFilter(price=priceIndex), page)
    salesData = salesListing.extractRawSalesData(
        rawSalesListingResp)
    saleList = salesData["salesList"]
    if not fileCreated and len(saleList) > 0:
        createEmptyCsvWithHeaders(fileName, saleList[0].keys())
        fileCreated = True
    elif len(saleList) > 0:
        appendRowsToCsv(fileName, saleList[0].keys(), saleList)
    return salesData, fileCreated


if __name__ == "__main__":
    # examples, chatswood, st leonards, willoughby
    inputSuburb = input("Enter a NSW Suburb (Spelling is critical): ")
    priceIndex = int(input("Enter an appropriate minimum price: "))
    fileName = f'./data/{inputSuburb.lower().replace(" ", "_")}_sales_list_{date.today()}.csv'
    fileCreated = False
    salesListing = SalesListing(baseURL, headers)
    while salesListing.nextIncrement != 0:  # loops through all the price ranges
        salesData, fileCreated = getSalesDataAndSaveToCSV(
            inputSuburb, priceIndex, fileName, fileCreated, 1)
        salesSummaryData = salesData["salesSummaryData"]

        # Loop through all pagination & obtain all sales property listing
        for page in tqdm(range(2, salesSummaryData["totalPages"] + 1)):
            getSalesDataAndSaveToCSV(
                inputSuburb, priceIndex, fileName, fileCreated, page)
            # performing a sleeper just so we dont spam domain and get banned
            time.sleep(random.randint(1, 2))

        priceIndex = priceIndex + \
            salesListing.nextIncrement if salesListing.nextIncrement is not None else 0
