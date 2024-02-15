import requests
from dataclasses import dataclass
from typing import Optional, TypeAlias, Dict
import csv

baseURL = 'https://www.domain.com.au/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/118.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br'
}

'''
filters - empty for all prices, <num>-<num> for range, and <num>-any for above
    price: usually 0 - millions range
    bedrooms: 1 - 5+
    carspaces: 0 - 3+
    bathrooms: 1 - 4+
'''


@dataclass
class SalesFilter:
    price: Optional[str] = None
    bedrooms: Optional[str] = None
    carspaces: Optional[str] = None
    bathrooms: Optional[str] = None


# Type Aliasing - https://docs.python.org/3/library/typing.html
SalesListingResp: TypeAlias = object
PropertyListingResp: TypeAlias = object


def loadNSWPostcodes():
    nswPostcodes = {}
    with open("./domain_python/nsw_postcode.csv", "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            locality = str(row['locality']).lower()
            nswPostcodes[locality] = row['postcode']
    return nswPostcodes


class DomainAdaptor:
    def __init__(self, baseURL=baseURL, headers=headers):
        self.baseURL = baseURL
        self.headers = headers
        self.nswPostcodes = loadNSWPostcodes()

    '''
    Sales Listing By Suburb
    Note: postcode search: https://www.domain.com.au/sale/?postcode=2150&excludeunderoffer=1
    '''

    def getSalesListingBySuburb(self, suburb: str = "parramatta", salesFilter: SalesFilter = SalesFilter(price="")):
        formattedSuburb = self.suburbFormatter(suburb)
        response = requests.get(baseURL + "sale/" + formattedSuburb +
                                '/?excludeunderoffer=1&sort=dateupdated-desc', headers=headers)
        if response.status_code != 200:
            raise Exception(
                f"status code is {response.status_code}. Could be something wrong with the suburb formatter.")
        else:
            return response

    '''
    Sales Listing By Suburb
    '''

    def getPropertyListing(self, propertyId: str) -> PropertyListingResp:
        response = requests.get(baseURL + propertyId, headers=headers)
        return response

    '''
    Helper Functions
    '''

    def suburbFormatter(self, suburb: str, state: str = "NSW") -> str:
        if suburb.lower() in self.nswPostcodes.keys():
            formattedSuburb = f'{suburb}-{state}-{self.nswPostcodes[suburb]}'
            return formattedSuburb
        else:
            raise Exception(f"suburb: {suburb} could not be found")


if __name__ == "__main__":
    doaminAdaptor = DomainAdaptor(baseURL, headers)
    salesListing = doaminAdaptor.getSalesListingBySuburb()
    propertyListing = doaminAdaptor.getPropertyListing("2018791254")
    print("script completed")
