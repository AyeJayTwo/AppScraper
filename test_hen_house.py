from scrapers.ios_scraper import IOSScraper

def main():
    scraper = IOSScraper()
    retailer_name = "Hen House"
    app_url = "https://apps.apple.com/us/app/hen-house-market/id6446866698"
    
    result = scraper.scrape_retailer_app(retailer_name, app_url)
    
    if result:
        print(f"Retailer: {result['retailer_name']}")
        print(f"App ID: {result['app_id']}")
        print(f"Rating: {result['score']}")
        print(f"Number of Reviews: {result['review_count']}")
    else:
        print("Failed to scrape app data")

if __name__ == "__main__":
    main() 