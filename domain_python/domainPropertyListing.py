import jmespath
from domainAdaptor import DomainAdaptor


class PropertyListing(DomainAdaptor):
    def extractRawPropertyData(self, rawPropertyResp) -> dict:
        '''
            Brute Force Way of obtaining object of the propertyListing
        '''
        rawNextData = self.extractNextDataFromResp(rawPropertyResp.text)
        componentProps = jmespath.search(
            "props.pageProps.componentProps", rawNextData)
        propertyId = componentProps["listingId"]
        layoutProps = jmespath.search(
            "props.pageProps.layoutProps", rawNextData)
        propertyListing = componentProps["listingsMap"][str(propertyId)]
        return {"propertyId": propertyId,
                "listingUrl": propertyListing["listingModel"]["url"],
                "title": layoutProps['title'],
                "description": layoutProps['description'],
                "address": componentProps["listingSummary"]["address"],
                "bedrooms": componentProps["listingSummary"]["beds"],
                "bathrooms": componentProps["listingSummary"]["baths"],
                "parking": componentProps["listingSummary"]["parking"],
                "propertyType": componentProps["listingSummary"]["propertyType"],
                "status": componentProps["listingSummary"]["status"],
                "mode": componentProps["listingSummary"]["mode"],
                "agent": {
                    "agency": componentProps["priceGuide"]["agencyName"],
                    "agents": jmespath.search("agents[*].name", componentProps),
                    "agencyProfileUrl": componentProps["agencyProfileUrl"],
                    "propertyDeveloperUrl": componentProps["propertyDeveloperUrl"],
                },
                "priceGuide": propertyListing["listingModel"]["price"],
                "landSize": propertyListing["listingModel"]["features"]["landSize"],
                "landUnit": propertyListing["listingModel"]["features"]["landUnit"],
                "estimatedPriceFrom": componentProps["priceGuide"]["estimatedPrice"]["from"],
                "estimatedPriceTo": componentProps["priceGuide"]["estimatedPrice"]["to"],
                "features": componentProps["features"],
                "schoolCatchment": componentProps["schoolCatchment"],
                "latitude": componentProps["map"]["latitude"],
                "longitude": componentProps["map"]["longitude"],
                "createdOn": componentProps["createdOn"],
                "domainSays": {
                    "firstListedDate": componentProps["domainSays"]["firstListedDate"],
                    "lastSoldOnDate": componentProps["domainSays"]["lastSoldOnDate"],
                    "medianRentPrice": componentProps["domainSays"]["medianRentPrice"],
                    "numberSold": componentProps["domainSays"]["numberSold"],
                    "propertyCategoryForSale": componentProps["domainSays"]["propertyCategoryForSale"],
                    "soldPropertiesUrl": componentProps["domainSays"]["soldPropertiesUrl"],
                    "domainSaysUpdatedDate": componentProps["domainSays"]["updatedDate"],
                    "storyPropertyType": componentProps["domainSays"]["storyPropertyType"],
                    "propertyBedrooms": componentProps["domainSays"]["propertyBedrooms"]},
                "suburbInsights": {
                    "bedrooms": componentProps["suburbInsights"]["beds"],
                    "propertyType": componentProps["suburbInsights"]["propertyType"],
                    "suburb": componentProps["suburbInsights"]["suburb"],
                    "medianPrice": componentProps["suburbInsights"]["medianPrice"],
                    "avgDaysOnMarket": componentProps["suburbInsights"]["avgDaysOnMarket"],
                    "auctionClearance": componentProps["suburbInsights"]["auctionClearance"],
                    "nrSoldThisYear": componentProps["suburbInsights"]["nrSoldThisYear"],
                    "entryLevelPrice": componentProps["suburbInsights"]["entryLevelPrice"],
                    "luxuryLevelPrice": componentProps["suburbInsights"]["luxuryLevelPrice"],
                    "renterPercentage": componentProps["suburbInsights"]["renterPercentage"],
                    "singlePercentage": componentProps["suburbInsights"]["singlePercentage"],
                    "demographics": {
                        "population": componentProps["suburbInsights"]["demographics"]["population"],
                        "avgAge": componentProps["suburbInsights"]["demographics"]["avgAge"],
                        "owners": componentProps["suburbInsights"]["demographics"]["owners"],
                        "renters": componentProps["suburbInsights"]["demographics"]["renters"],
                        "families": componentProps["suburbInsights"]["demographics"]["families"],
                        "singles": componentProps["suburbInsights"]["demographics"]["singles"]
                    },
                    "salesGrowthList": componentProps["suburbInsights"]["salesGrowthList"]
                }
                }
