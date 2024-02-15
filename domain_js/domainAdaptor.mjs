import puppeteer from "puppeteer";
import path from "path";
import fs from "fs";
import { fileURLToPath } from "url";
import { JSDOM } from "jsdom";

const baseURL = "https://www.domain.com.au/";
const headers = {
  "User-Agent":
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/118.0",
  Accept:
    "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
  "Accept-Language": "en-US,en;q=0.5",
  "Accept-Encoding": "gzip, deflate, br",
};

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
export async function getSalesListingBySuburb(formattedSuburb) {
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();
  const url = `${baseURL}sale/${formattedSuburb}/?excludeunderoffer=1&sort=dateupdated-desc`;
  await page.goto(url);
  await page; // Wait for the navigation to complete
  const element = await page.waitForSelector("div");
  //   const evaluate = await page.evaluate();
  const htmlContent = await page.content();

  // Save the HTML content to a file
  fs.writeFileSync(
    `puppeter_${formattedSuburb}.html`,
    htmlContent,
    "utf8",
    (err) => {
      if (err) {
        console.error("Error writing to file:", err);
      } else {
        console.log("DOM content has been saved to output.html");
      }
    }
  );
  // close the browser
  await browser.close();

  return page;
}

export async function saveHtmlToPDF() {
  // save content to pdf
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();
  const html = fs.readFileSync(
    `${__dirname}/samples/sampleSalesListingPage2.html`,
    "utf8"
  );
  await page.setContent(html, {
    waitUntil: "domcontentloaded",
  });
  // create a pdf buffer
  const pdfBuffer = await page.pdf({
    format: "A4",
  });

  // or a .pdf file
  await page.pdf({
    format: "A4",
    path: `${__dirname}/pageResponse.pdf`,
  });
}

export function convertHtmlToDom() {
  const html = fs.readFileSync(
    `${__dirname}/samples/sampleSalesListingPage2.html`,
    "utf8"
  );
  const dom = new JSDOM(html);
  const { document } = dom.window;
  const divElement = document.querySelector("#myDiv");
  const updatedHtml = dom.serialize();
  // Save the HTML content to a file
  fs.writeFileSync("domOutput_test.html", updatedHtml, "utf8", (err) => {
    if (err) {
      console.error("Error writing to file:", err);
    } else {
      console.log("DOM content has been saved to output.html");
    }
  });
}
