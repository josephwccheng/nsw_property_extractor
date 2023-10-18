from domainAdaptor import DomainAdaptor
from domainSalesListing import SalesListing


if __name__ == "__main__":
    inputSuburb = "PARRAMATTA".lower()
    domainAdaptor = DomainAdaptor()
    salesListing = SalesListing()
    salesResp = domainAdaptor.getSalesListingBySuburb(inputSuburb)
    salesListing.extractRawData(salesResp)
    print("done for now")
