from domainAdaptor import DomainAdaptor, SalesFilter
from domainSalesListing import SalesListing
import time
import random
import csv

if __name__ == "__main__":
    inputSuburb = "PARRAMATTA".lower()
    domainAdaptor = DomainAdaptor()
    salesListing = SalesListing()
    # Query Domain website via the suburb
    rawSalesListingResp = domainAdaptor.getSalesListingBySuburb(inputSuburb)
    # Extract data from sales listing page
    rawData = salesListing.extractRawSalesData(rawSalesListingResp)
    digitalData = rawData['digitalData']
    # Obtain the total pagination pages and total results of the search
    totalPaginationPages = digitalData['totalPaginatePages']
    totalResult = digitalData['totalResult']
    # obtain high level property list and store it locally
    salesList = rawData['salesList']
    page = 1
    allSalesList = salesListing.filterPropertyWithId(salesList, page)
    # Loop through all pagination & obtain all sales property listing
    for page in range(2, 10):  # totalPaginationPages
        rawSalesListingResp = domainAdaptor.getSalesListingBySuburb(
            inputSuburb, SalesFilter(price=""), page)
        rawData = salesListing.extractRawSalesData(rawSalesListingResp)
        digitalData = rawData['digitalData']
        salesList = rawData['salesList']
        allSalesList = allSalesList + salesListing.filterPropertyWithId(
            salesList, page)
        # performing a sleeper just so we dont spam domain and get banned
        time.sleep(random.randint(1, 2))
        print(f"page {page} extracted")

    with open('step_3.csv', 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, allSalesList[0].keys())
        dict_writer.writeheader()
        dict_writer.writerows(allSalesList)
