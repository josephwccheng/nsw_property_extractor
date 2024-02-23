import jmespath
from domainAdaptor import DomainAdaptor
from datetime import date
import time
import random
from tqdm import tqdm
from fileProcessing import createEmptyCsvWithHeaders, appendRowsToCsv


class SoldListing(DomainAdaptor):
    '''
    Domain Sold Listing page
    Note: ipAddress is being tracked
    '''

    def extractRawSoldData(self, rawsoldListingResp) -> dict:
        '''
            Brute Force Way of obtaining object of the sold
        '''
        rawNextData = self.extractNextDataFromResp(rawsoldListingResp.text)
        componentProps = jmespath.search(
            "props.pageProps.componentProps", rawNextData)
        listingsMap = componentProps["listingsMap"]
        soldPropertyList = []
        for propertyId in listingsMap:
            listingType = listingsMap[propertyId]["listingType"]
            if listingType != "listing":
                continue
            propertyData = listingsMap[propertyId]["listingModel"]
            address = propertyData["address"]
            features = propertyData["features"]
            soldPropertyList.append({
                "propertyId": propertyId,
                "listingUrl": f'{self.baseURL}{propertyData["url"][1:]}',
                "address": f'{address["street"]},{address["suburb"]},{address["state"]},{address["postcode"]}',
                "suburb": address["suburb"],
                "bedrooms": features["beds"] if "beds" in features else "N/A",
                "bathrooms": features["baths"] if "baths" in features else "N/A",
                "parking": features["parking"] if "parking" in features else 0,
                "propertyType": features["propertyType"],
                "landSize": features["landSize"],
                "landUnit": features["landUnit"],
                "price": self.extractPriceFromRawGuides(propertyData["price"]),
                "priceOrig": propertyData["price"],
                "agents": propertyData["branding"]["agentNames"] if "branding" in propertyData else "",
                "agency": propertyData["branding"]["brandName"] if "branding" in propertyData else propertyData["projectName"],
                # "propertyTypeFormatted": features["propertyTypeFormatted"],
                # "latitude": address["lat"] if "lat" in address else "N/A",
                # "longitude": address["lng"] if "lng" in address else "N/A",
            })
        soldSummaryData = {
            "totalListings": componentProps["totalListings"],
            "currentPage": componentProps["currentPage"],
            "totalPages": componentProps["totalPages"],
            "searchTerm": componentProps["defaultSavedSearchName"],
            "suburb": componentProps["suburb"]["suburb"]["name"] if "suburb" in componentProps["suburb"] else "",
            "listUrl": componentProps["listUrl"],
            "listingType": componentProps["pageViewMetadata"]["searchRequest"]["listingType"],
            "propertyCounts": componentProps["propertyCounts"]
        }

        return {"soldSummaryData": soldSummaryData, "soldList": soldPropertyList}

    def extractDigitalData(self, digitalData):
        search = digitalData["page"]["pageInfo"]["search"]
        return {
            "totalPaginatePages": search["resultsPages"],
            "totalResult": search["searchResultCount"],
            "resultsRecord": search["resultsRecords"].split(',')
        }

    def extractsoldList(self, rawPropertyList) -> list:
        propertyList = []
        for property in rawPropertyList[1:]:
            match property["@type"]:
                case 'Event':
                    location = property['location']
                    propertyList.append({
                        "propertyType": location['@type'],
                        "propertyId": property['url'].split("-")[-1],
                        "name": property['name'],
                        "description": property['description'],
                        "url": property['url'],
                        "startDate": property['startDate'],
                        "geoCoordinates": {
                            "latitude": location['geo']['latitude'],
                            "longitude": location['geo']['longitude']
                        },
                        "address": {
                            "streetAddress": location['address']['streetAddress'],
                            "postalCode": location['address']['postalCode'],
                            "state": location['address']['addressRegion'],
                            "suburb": location['address']['addressLocality'],
                        }
                    })
                case 'Residence':
                    propertyList.append({
                        "propertyType": property["@type"],
                        "address": {
                            "streetAddress": property['address']['streetAddress'] if 'streetAddress' in property['address'] else "",
                            "postalCode": property['address']['postalCode'] if 'postalCode' in property['address'] else "",
                            "state": property['address']['addressRegion'] if 'addressRegion' in property['address'] else "",
                            "suburb": property['address']['addressLocality'] if 'addressLocality' in property['address'] else "",
                        }
                    })
                case _:
                    print(f'{property["@type"]} not captured')
        return propertyList


if __name__ == "__main__":
    baseURL = 'https://www.domain.com.au/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/118.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br'
    }
    # examples, chatswood, st leonards, willoughby
    inputSuburb = input("Enter a NSW Suburb (Spelling is critical): ")
    fileName = f'{inputSuburb.lower().replace(" ", "_")}_sold_list_{date.today()}.csv'
    soldListing = SoldListing(baseURL, headers)
    rawSoldListingResp = soldListing.getSoldListingBySuburb(inputSuburb)
    soldData = soldListing.extractRawSoldData(
        rawSoldListingResp)
    soldSummaryData = soldData["soldSummaryData"]
    soldList = soldData["soldList"]
    createEmptyCsvWithHeaders(fileName, soldList[0].keys())
    appendRowsToCsv(fileName, soldList[0].keys(), soldList)
    # Loop through all pagination & obtain all sold property listing
    for page in tqdm(range(2, soldSummaryData["totalPages"] + 1)):
        rawSoldListingResp = soldListing.getSoldListingBySuburb(
            inputSuburb, page)
        soldList = soldListing.extractRawSoldData(
            rawSoldListingResp)['soldList']
        appendRowsToCsv(fileName, soldList[0].keys(), soldList)
        # performing a sleeper just so we dont spam domain and get banned
        time.sleep(random.randint(1, 3))

    print(f"completed with sold summary data: {soldSummaryData}")


'''
Backup codes
    Attempt 1
    # resp = rawsoldListingResp.text
    # soup = BeautifulSoup(resp, 'html.parser')
    # allScripts = soup.findAll(
    #     'script')
    # digitalDataSearch = "var digitalData = "
    # digitalDataScript = [
    #     script.text for script in allScripts if digitalDataSearch in script.text]
    # digitalData = re.search(
    #     r"({.*?});", digitalDataScript[0])  # type: ignore
    # if not digitalData:
    #     raise FileNotFoundError("Could not extract the reggex phrase")
    # digitalData = self.extractDigitalData(
    #     json.loads(digitalData[0].rstrip(";")))

    # bodyTypeSearch = "application/ld+json"
    # bodyScript = soup.find('script', type=bodyTypeSearch)
    # if bodyScript == None:
    #     raise FileNotFoundError("Body Script is null")
    # soldList = self.extractsoldList(json.loads(bodyScript.text))
    # filteredsoldList = [
    #     property for property in soldList if "propertyId" in property]

'''
