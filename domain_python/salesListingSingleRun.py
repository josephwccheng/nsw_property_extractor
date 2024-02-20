from domainAdaptor import DomainAdaptor
from domainSalesListing import SalesListing

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
    proprtyList = rawData['proprtyList']
    page = 1
    allPropertyList = salesListing.filterPropertyWithId(proprtyList, page)
    print(f'pagePropertyList is: {allPropertyList}')
