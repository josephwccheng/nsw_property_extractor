import json
import re
from bs4 import BeautifulSoup
import requests
from dataclasses import dataclass
from typing import Optional, TypeAlias, Dict
import csv

'''
filters - empty for all prices, <num>-<num> for range, and <num>-any for above
    price: usually 0 - millions range
    bedrooms: 1 - 5+
    carspaces: 0 - 3+
    bathrooms: 1 - 4+
'''


@dataclass
class SalesFilter:
    price: Optional[int] = None
    bedrooms: Optional[str] = None
    carspaces: Optional[str] = None
    bathrooms: Optional[str] = None
    sortNewest: Optional[bool] = True
    suburbExclusive: Optional[bool] = True


# Type Aliasing - https://docs.python.org/3/library/typing.html
SalesListingResp: TypeAlias = object
PropertyListingResp: TypeAlias = object
RawNextResp: TypeAlias = object


def loadNSWPostcodes():
    nswPostcodes = {}
    with open("./domain/nsw_postcode.csv", "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            locality = str(row['locality']).lower()
            nswPostcodes[locality] = row['postcode']
    return nswPostcodes


class DomainAdaptor:
    def __init__(self, baseURL, headers):
        self.baseURL = baseURL
        self.headers = headers
        self.nswPostcodes = loadNSWPostcodes()
        self.priceFilterMapping = {
            "300000-1000000": 50000,
            "1000000-3000000": 100000,
            "3000000-5000000": 250000,
            "5000000-12000000": 500000,
        }
        self.nextIncrement = None
        self.priceRange = None

    '''
    Sales Listing By Suburb
    Note: postcode search: https://www.domain.com.au/sale/?postcode=2150&excludeunderoffer=1
    '''

    def getSalesListingBySuburb(self, suburb: str = "parramatta", salesFilter: SalesFilter = SalesFilter(sortNewest=True, suburbExclusive=True), page=1):
        formattedSuburb = self.suburbFormatter(suburb)
        # Note: sort = dateupdated-desc is sorting by the newest property
        # there's some funny thing going on with &lastsearchdate=2024-02-22t16:09:09.740z
        url = f'{self.baseURL}sale/{formattedSuburb}/?excludeunderoffer=1'
        if salesFilter.price:
            self.priceRange = self.priceRangeCalc(salesFilter.price)
            url = f'{url}&price={self.priceRange}'
        if salesFilter.sortNewest:
            url = f'{url}&sort=dateupdated-desc'
        if salesFilter.suburbExclusive:
            url = f'{url}&ssubs=0'
        if page > 1:
            url = url + f'{url}&page={page}'
        print(f'url is {url}')
        response = requests.get(url, headers=self.headers)

        if response.status_code != 200:
            raise Exception(
                f"status code is {response.status_code}. Could be something wrong with the suburb formatter.")
        else:
            return response

    def get(self, url: str):
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            raise Exception(
                f"status code is {response.status_code}. Could be something wrong with the url for property listing.")
        else:
            return response

    def getPropertyListingById(self, propertyId: str) -> PropertyListingResp:
        response = requests.get(
            self.baseURL + propertyId, headers=self.headers)
        if response.status_code != 200:
            raise Exception(
                f"status code is {response.status_code}. Could be something wrong with the property id for property listing.")
        else:
            return response

    def getSoldListingBySuburb(self, suburb: str = "parramatta", page=1):
        formattedSuburb = self.suburbFormatter(suburb)
        # Note: default sorted by sales date
        url = f'{self.baseURL}sold-listings/{formattedSuburb}/house/?excludepricewithheld=1'
        if page > 1:
            url = url + f'{url}&page={page}'
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            raise Exception(
                f"status code is {response.status_code}. Could be something wrong with the suburb formatter.")
        else:
            return response

    '''
    Helper Functions
    '''

    def suburbFormatter(self, suburb: str, state: str = "NSW") -> str:
        if suburb.lower() in self.nswPostcodes.keys():
            suburbText = suburb.lower().replace(" ", "-")
            formattedSuburb = f'{suburbText}-{state}-{self.nswPostcodes[suburb.lower()]}'
            return formattedSuburb
        else:
            raise Exception(f"suburb: {suburb} could not be found")

    def extractNextDataFromResp(self, rawListingResp) -> RawNextResp:
        soup = BeautifulSoup(rawListingResp, 'html.parser')
        nextDataSearch = '__NEXT_DATA__'
        script = soup.find(
            'script', id=nextDataSearch)
        if not script:
            raise FileNotFoundError(
                f"Could not find the element {nextDataSearch} could be something wrong in the html response")
        return json.loads(script.text)

    def extractPriceFromRawGuides(self, rawPriceGuide: str) -> str:
        prices = re.findall(r"[$]\S*", rawPriceGuide)  # type: ignore
        price = ""
        if len(prices) > 0:
            price = '-'.join(prices)
        return price

    def priceRangeCalc(self, price: int, priceMin=300000, priceMax=12000000) -> str:
        if price < priceMin:
            self.nextIncrement = 0
            return f'0-{priceMin}'
        elif price >= priceMax:
            self.nextIncrement = 0
            return f'{priceMax}-any'
        keys = self.priceFilterMapping.keys()
        for key in keys:
            lowerRange, upperRange = key.split('-')
            if price >= int(lowerRange) and price < int(upperRange):
                self.nextIncrement = int(self.priceFilterMapping[key])
                lowerBound = price
                upperBound = price + self.nextIncrement - 1
                return f'{lowerBound}-{upperBound}'
        raise ValueError("Price range value is not correct")


if __name__ == "__main__":
    baseURL = 'https://www.domain.com.au/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/118.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br'
    }
    doaminAdaptor = DomainAdaptor(baseURL, headers)
    salesListing = doaminAdaptor.getSalesListingBySuburb(
        "parramatta", SalesFilter(price=0, sortNewest=True, suburbExclusive=True))
    salesListing = doaminAdaptor.getSalesListingBySuburb()
    propertyListing = doaminAdaptor.getPropertyListingById("2018791254")
    print("script completed")
