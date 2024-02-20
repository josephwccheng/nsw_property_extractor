from domainAdaptor import DomainAdaptor
from domainPropertyListing import PropertyListing

if __name__ == "__main__":
    propertyUrl = "https://www.domain.com.au/2-108-120-station-street-wentworthville-nsw-2145-2017150237"
    domainAdaptor = DomainAdaptor()
    propertyListing = PropertyListing()
    rawPropertyResp = domainAdaptor.getPropertyListing(propertyUrl)
    propertyData = propertyListing.extractRawPropertyData(rawPropertyResp)
    print("finish")
