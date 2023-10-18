import json


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

    def extractRawData(self, rawSalesListingResp):
        '''
            Brute Force Way of obtaining object of the sales
        '''
        resp = rawSalesListingResp.text
        start = "var digitalData = "
        end = "var dataLayer"
        filteredMeta = resp.replace("\n", " ")
        filteredMeta = filteredMeta.split(start)[1]
        filteredMeta = filteredMeta.split(end)[0]
        filteredMeta = filteredMeta.replace(";", "")
        filteredMeta = filteredMeta.replace("\'", "\"")

        metaData = self.extractDigitalData(json.loads(filteredMeta))

        start = '<script type="application/ld+json">'
        end = '</script>'
        filteredBody = rawSalesListingResp.text.replace("\n", " ")
        filteredBody = filteredBody.split(start)[1]
        filteredBody = filteredBody.split(end)[0]
        filteredBody = filteredBody.replace(";", "")
        filteredBody = filteredBody.replace("\'", "\"")

        body = self.extractPropertyList(json.loads(filteredBody))

        return {"digitalData": metaData, "proprtyList": body}

    def extractDigitalData(self, digitalData):
        search = digitalData["page"]["pageInfo"]["search"]
        return {
            "totalPaginatePages": search["resultsPages"],
            "totalResult": search["searchResultCount"],
            "resultsRecord": search["resultsRecords"].split(',')
        }

    def extractPropertyList(self, propertyList):
        output = []
        for property in propertyList[1:]:
            match property["@type"]:
                case 'Event':
                    location = property['location']
                    output.append({
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
                    output.append({
                        "propertyType": property["@type"],
                        "address": {
                            "streetAddress": property['address']['streetAddress'],
                            "postalCode": property['address']['postalCode'],
                            "state": property['address']['addressRegion'],
                            "suburb": property['address']['addressLocality'],
                        }
                    })
                case _:
                    print(f'{property["@type"]} not captured')
        return output
