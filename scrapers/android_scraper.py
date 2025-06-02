import logging
from typing import Dict, Optional
import re
from google_play_scraper import app as gp_app

class AndroidScraper:
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def extract_app_id(self, url: str) -> Optional[str]:
        """
        Extract the app ID from a Google Play Store URL.
        """
        try:
            match = re.search(r'id=([\w\.]+)', url)
            if match:
                return match.group(1)
            return None
        except Exception as e:
            self.logger.error(f"Error extracting app ID from URL {url}: {str(e)}")
            return None

    def get_app_ratings(self, app_id: str) -> Optional[Dict]:
        """
        Fetch Android app ratings from the Google Play Store using google_play_scraper.
        """
        try:
            result = gp_app(app_id, lang='en', country='us')
            rating = result.get('score')
            review_count = result.get('ratings')
            if rating is None or review_count is None:
                self.logger.error(f"Could not find rating or review count for app {app_id}")
                return None
            return {
                'score': rating,
                'review_count': review_count
            }
        except Exception as e:
            self.logger.error(f"Error fetching app data for {app_id}: {str(e)}")
            return None

    def scrape_retailer_app(self, retailer_name: str, app_url: str) -> Optional[Dict]:
        app_id = self.extract_app_id(app_url)
        if not app_id:
            self.logger.error(f"Could not extract app ID from URL: {app_url}")
            return None
        ratings = self.get_app_ratings(app_id)
        if not ratings:
            return None
        return {
            'retailer_name': retailer_name,
            'app_id': app_id,
            'score': ratings['score'],
            'review_count': ratings['review_count']
        } 