import json
from bs4 import BeautifulSoup
import re


class SalesListing():
    '''
    Domain Sales Listing page
        Inspection / Auction -> event
        Other's wont be in the 	record, but will be in list
    digitalData - object
        Search = [page -> pageInfo -> search]
        - TotalPaginatePage = [Search - resultsPages]
        - Total Result = [Search -> searchResultCount]
        - Data with price = [Search -> resultsRecords]
        - Data without price = [Search -> resultsRecords1]
    proprtyList - list[object]
        ignore first index
        - propertyType = [location -> @type]
        - geoCoordinates = [location -> geo]
            - latitude
            - longitude
        - address = [address]
            - streetAddress
            - postalCode
            - addressLocality
            - addressRegion
        - name
        - description
        - url
        - propertyID - obtain from end of url (reggex)
    Note: ipAddress is being tracked
    '''

    def extractRawSalesData(self, rawSalesListingResp) -> dict:
        '''
            Brute Force Way of obtaining object of the sales
        '''
        resp = rawSalesListingResp.text
        soup = BeautifulSoup(resp, 'html.parser')
        allScripts = soup.findAll(
            'script')
        digitalDataSearch = "var digitalData = "
        digitalDataScript = [
            script.text for script in allScripts if digitalDataSearch in script.text]
        digitalData = re.search(
            r"({.*?});", digitalDataScript[0])  # type: ignore
        if not digitalData:
            raise FileNotFoundError("Could not extract the reggex phrase")
        metaData = self.extractDigitalData(
            json.loads(digitalData[0].rstrip(";")))

        bodyTypeSearch = "application/ld+json"
        bodyScript = soup.find('script', type=bodyTypeSearch)
        if bodyScript == None:
            raise FileNotFoundError("Body Script is null")
        body = self.extractPropertyList(json.loads(bodyScript.text))
        return {"digitalData": metaData, "salesList": body}

    def extractDigitalData(self, digitalData):
        search = digitalData["page"]["pageInfo"]["search"]
        return {
            "totalPaginatePages": search["resultsPages"],
            "totalResult": search["searchResultCount"],
            "resultsRecord": search["resultsRecords"].split(',')
        }

    def extractPropertyList(self, rawPropertyList) -> list:
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

    def filterPropertyWithId(self, propertyList, page=1) -> list:
        pagePropertyList = []
        for property in propertyList:
            if "propertyId" in property:
                property['page'] = page
                pagePropertyList.append(property)
        return pagePropertyList
