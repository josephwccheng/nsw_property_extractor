import jmespath
from domainAdaptor import DomainAdaptor


class SalesListing(DomainAdaptor):
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
        # Attempt 1
        # resp = rawSalesListingResp.text
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
        # salesList = self.extractSalesList(json.loads(bodyScript.text))
        # filteredSalesList = [
        #     property for property in salesList if "propertyId" in property]
        # Attempt 2
        rawNextData = self.extractNextDataFromResp(rawSalesListingResp.text)
        componentProps = jmespath.search(
            "props.pageProps.componentProps", rawNextData)
        listingsMap = componentProps["listingsMap"]
        salesPropertyList = []
        for propertyId in listingsMap:
            listingType = listingsMap[propertyId]["listingType"]
            if listingType != "listing":
                continue
            propertyData = listingsMap[propertyId]["listingModel"]
            address = propertyData["address"]
            features = propertyData["features"]
            salesPropertyList.append({
                "propertyId": propertyId,
                "listingUrl": f'{self.baseURL}{propertyData["url"][1:]}',
                "address": f'{address["street"]},{address["suburb"]},{address["state"]},{address["postcode"]}',
                "bedrooms": features["beds"] if "beds" in features else "N/A",
                "bathrooms": features["baths"] if "baths" in features else "N/A",
                "parking": features["parking"] if "parking" in features else 0,
                "propertyType": features["propertyType"],
                "propertyTypeFormatted": features["propertyTypeFormatted"],
                "landSize": features["landSize"],
                "landUnit": features["landUnit"],
                "latitude": address["lat"] if "lat" in address else "N/A",
                "longitude": address["lng"] if "lng" in address else "N/A",
                "price": self.extractPriceFromRawGuides(propertyData["price"]),
                "agent": {
                    "agents": propertyData["branding"]["agentNames"] if "branding" in propertyData else "",
                    "agency": propertyData["branding"]["brandName"] if "branding" in propertyData else propertyData["projectName"],
                }
            })

        # layoutProps = jmespath.search(
        #     "props.pageProps.layoutProps", rawNextData)
        salesSummaryData = {
            "totalListings": componentProps["totalListings"],
            "currentPage": componentProps["currentPage"],
            "totalPages": componentProps["totalPages"],
            "searchTerm": componentProps["defaultSavedSearchName"],
            "suburb": componentProps["suburb"]["suburb"]["name"],
            "listUrl": componentProps["listUrl"],
            "listingType": componentProps["pageViewMetadata"]["searchRequest"]["listingType"],
            "propertyCounts": componentProps["propertyCounts"]
        }

        return {"salesSummaryData": salesSummaryData, "salesList": salesPropertyList}

    def extractDigitalData(self, digitalData):
        search = digitalData["page"]["pageInfo"]["search"]
        return {
            "totalPaginatePages": search["resultsPages"],
            "totalResult": search["searchResultCount"],
            "resultsRecord": search["resultsRecords"].split(',')
        }

    def extractSalesList(self, rawPropertyList) -> list:
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
