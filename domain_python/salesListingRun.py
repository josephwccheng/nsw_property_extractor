from domainAdaptor import SalesFilter
from domainSalesListing import SalesListing
from datetime import date
import time
import random
import csv
from tqdm import tqdm

baseURL = 'https://www.domain.com.au/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/118.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br'
}

if __name__ == "__main__":
    inputSuburb = "ST LEONARDS"
    fileName = f'{inputSuburb.lower().replace(" ", "_")}_sales_list_{date.today()}.csv'
    salesListing = SalesListing(baseURL, headers)
    # Query Domain website via the suburb
    rawSalesListingResp = salesListing.getSalesListingBySuburb(inputSuburb)
    # Extract data from sales listing page
    salesData = salesListing.extractRawSalesData(
        rawSalesListingResp)
    salesSummaryData = salesData["salesSummaryData"]
    saleList = salesData["salesList"]
    # Create a CSV file and add the header in
    with open(fileName, 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, saleList[0].keys())
        dict_writer.writeheader()
    # Loop through all pagination & obtain all sales property listing
    for page in tqdm(range(2, salesSummaryData["totalPages"])):
        rawSalesListingResp = salesListing.getSalesListingBySuburb(
            inputSuburb, SalesFilter(price=""), page)
        saleList = salesListing.extractRawSalesData(
            rawSalesListingResp)['salesList']
        with open(fileName, 'a', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, saleList[0].keys())
            dict_writer.writerows(salesListing.extractRawSalesData(
                rawSalesListingResp)['salesList'])
        # performing a sleeper just so we dont spam domain and get banned
        time.sleep(random.randint(1, 3))
