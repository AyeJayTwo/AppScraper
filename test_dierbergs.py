from scrapers.android_scraper import AndroidScraper
from google_play_scraper import app as gp_app

def main():
    scraper = AndroidScraper()
    retailer_name = "Dierbergs"
    app_url = "https://play.google.com/store/apps/details?id=com.dierbergs.prod&hl=en_US"
    print(f"Testing URL: {app_url}")
    app_id = scraper.extract_app_id(app_url)
    print(f"Extracted app ID: {app_id}")
    try:
        result = gp_app(app_id, lang='en', country='us')
        print(f"Raw result: {result}")
        print(f"Retailer: {retailer_name}")
        print(f"App ID: {app_id}")
        print(f"Rating: {result.get('score')}")
        print(f"Number of Reviews: {result.get('ratings')}")
    except Exception as e:
        print(f"Error fetching app data for {app_id}: {e}")

if __name__ == "__main__":
    main() 