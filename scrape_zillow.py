from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd

def scrape_zillow(city="Dallas, TX", max_pages=1):
    listings = []
    city_url = city.replace(" ", "-").replace(",", "")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        for page_num in range(1, max_pages + 1):
            url = f"https://www.zillow.com/homes/for_rent/{city_url}/{page_num}_p/"
            print(f"Scraping page {page_num}: {url}")
            page.goto(url, timeout=60000)
            page.wait_for_timeout(4000)

            soup = BeautifulSoup(page.content(), "html.parser")
            cards = soup.select("article")

            for card in cards:
                address = card.select_one("address")
                price = card.select_one("span[data-test='property-card-price']")
                link = card.find("a", href=True)

                if address and price and link:
                    listings.append({
                        "address": address.text.strip(),
                        "price": price.text.strip(),
                        "link": "https://www.zillow.com" + link['href'].split('?')[0]
                    })

        browser.close()

    return pd.DataFrame(listings)

app = Flask(__name__)

@app.route("/scrape", methods=["GET"])
def scrape():
    city = request.args.get("city", "Dallas, TX")
    pages = int(request.args.get("pages", 1))
    df = scrape_zillow(city, max_pages=pages)
    return jsonify(df.to_dict(orient="records"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
