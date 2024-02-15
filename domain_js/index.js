import {
  getSalesListingBySuburb,
  saveHtmlToPDF,
  convertHtmlToDom,
} from "./domainAdaptor.mjs";

await getSalesListingBySuburb("parramatta-nsw-2150");

await saveHtmlToPDF();
convertHtmlToDom();
console.log("completed");
