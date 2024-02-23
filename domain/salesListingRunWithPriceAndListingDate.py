from domainPropertyListing import PropertyListing
from domainAdaptor import SalesFilter
from domainSalesListing import SalesListing
from datetime import date
import time
import random
from tqdm import tqdm
import pandas as pd
import os.path

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

    if not os.path.isfile(fileName):
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

    # Using the CSV as input, get the listing date info from property listing
    salesListing_df = pd.read_csv(fileName)
    # removing duplicates of propertyId based on some price ranges
    salesListing_dedup_df = salesListing_df.drop_duplicates(
        subset='propertyId', keep="last")
    firstListedDates = []
    for index, row in tqdm(salesListing_dedup_df.iterrows(), total=salesListing_dedup_df.shape[0]):
        propertyUrl = row["listingUrl"]
        propertyListing = PropertyListing(baseURL, headers)
        rawPropertyResp = propertyListing.get(propertyUrl)
        propertyData = propertyListing.extractRawPropertyData(rawPropertyResp)
        firstListedDates.append(propertyData["domainSays"]["firstListedDate"])
        # performing a sleeper just so we dont spam domain and get banned
        time.sleep(random.randint(1, 2))
    salesListing_dedup_df["firstListedDates"] = firstListedDates
    salesListing_dedup_df.to_csv(fileName, index=False)
    print("finish")
