from scrapers.android_scraper import AndroidScraper

def main():
    scraper = AndroidScraper()
    retailer_name = "Corner Rewards"
    app_url = "https://play.google.com/store/apps/details?id=com.skupos&hl=en_US"
    
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