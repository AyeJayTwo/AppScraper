import requests
from bs4 import BeautifulSoup
import logging
from typing import Dict, Optional
import re

class IOSScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def extract_app_id(self, url: str) -> Optional[str]:
        """
        Extract the app ID from an App Store URL.
        
        Args:
            url: The App Store URL
            
        Returns:
            The app ID if found, None otherwise
        """
        try:
            # Match patterns like /id123456789 or /app/name/id123456789
            match = re.search(r'/id(\d+)', url)
            if match:
                return match.group(1)
            return None
        except Exception as e:
            self.logger.error(f"Error extracting app ID from URL {url}: {str(e)}")
            return None

    def get_app_ratings(self, app_id: str) -> Optional[Dict]:
        """
        Scrape iOS app ratings from the App Store.
        
        Args:
            app_id: The App Store ID of the app
            
        Returns:
            Dict containing score and review_count, or None if scraping fails
        """
        try:
            url = f"https://apps.apple.com/us/app/id{app_id}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find the average rating
            rating_element = soup.find('span', class_='we-customer-ratings__averages__display')
            if not rating_element:
                self.logger.error(f"Could not find average rating for app {app_id}")
                return None
            rating = float(rating_element.text.strip())

            # Find the total ratings count
            count_element = soup.find('div', class_='we-customer-ratings__count small-hide medium-show')
            if not count_element:
                self.logger.error(f"Could not find ratings count for app {app_id}")
                return None
            # Remove commas and non-digit characters
            review_count = int(''.join(filter(str.isdigit, count_element.text)))

            return {
                'score': rating,
                'review_count': review_count
            }
            
        except requests.RequestException as e:
            self.logger.error(f"Network error while scraping app {app_id}: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"Error scraping app {app_id}: {str(e)}")
            return None

    def scrape_retailer_app(self, retailer_name: str, app_url: str) -> Optional[Dict]:
        """
        Scrape app ratings for a retailer's iOS app.
        
        Args:
            retailer_name: Name of the retailer
            app_url: URL of the app in the App Store
            
        Returns:
            Dict containing retailer name, app ID, score, and review count, or None if scraping fails
        """
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