import puppeteer from "puppeteer";
import { getSalesListingBySuburb } from "./domainAdaptor.mjs";
const baseURL = "https://www.domain.com.au/";
const headers = {
  "User-Agent":
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/118.0",
  Accept:
    "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
  "Accept-Language": "en-US,en;q=0.5",
  "Accept-Encoding": "gzip, deflate, br",
};

const browser = await puppeteer.launch();
const page = await browser.newPage();
await page.goto("https://developer.chrome.com/");
await getSalesListingBySuburb();
console.log("test");
