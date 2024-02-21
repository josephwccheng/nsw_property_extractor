from domainAdaptor import DomainAdaptor
from domainPropertyListing import PropertyListing

baseURL = 'https://www.domain.com.au/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/118.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br'
}

if __name__ == "__main__":
    propertyUrl = "https://www.domain.com.au/2019049915"
    propertyListing = PropertyListing(baseURL, headers)
    rawPropertyResp = propertyListing.getPropertyListing(propertyUrl)
    propertyData = propertyListing.extractRawPropertyData(rawPropertyResp)
    print("finish")
