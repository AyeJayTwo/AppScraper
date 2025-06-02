import csv
from typing import Dict, List, Optional
from scrapers.ios_scraper import IOSScraper
from scrapers.android_scraper import AndroidScraper
import logging
from database.db_utils import get_todays_rating, save_rating
from database.models import init_db
import pandas as pd
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RetailerRatings:
    def __init__(self):
        self.ios_scraper = IOSScraper()
        self.android_scraper = AndroidScraper()
        init_db()  # Ensure DB is initialized

    def process_retailer(self, retailer_name: str, ios_url: str, android_url: str) -> dict:
        """
        Process a single retailer's ratings from both iOS and Android.
        Returns a dictionary with the retailer's rating data.
        """
        # Check if we already have today's rating
        existing_rating = get_todays_rating(retailer_name)
        if existing_rating:
            logger.info(f"Using cached rating for {retailer_name}")
            return existing_rating

        # Get iOS ratings
        ios_data = self.ios_scraper.get_app_ratings(ios_url)
        if not ios_data:
            logger.error(f"Could not get iOS ratings for {retailer_name}")
            return None

        # Get Android ratings
        android_data = self.android_scraper.get_app_ratings(android_url)
        if not android_data:
            logger.error(f"Could not get Android ratings for {retailer_name}")
            return None

        # Store raw scores and reviews
        ios_score = ios_data['score']
        ios_reviews = ios_data['reviews']
        android_score = android_data['score']
        android_reviews = android_data['reviews']

        # Calculate overall weighted average
        total_reviews = ios_reviews + android_reviews
        if total_reviews > 0:
            weighted_average = (
                (ios_score * ios_reviews + android_score * android_reviews)
                / total_reviews
            )
        else:
            weighted_average = 0

        rating_data = {
            'retailer_name': retailer_name,
            'ios_url': ios_url,
            'android_url': android_url,
            'ios_score': ios_score,  # Store raw score
            'ios_reviews': ios_reviews,
            'android_score': android_score,  # Store raw score
            'android_reviews': android_reviews,
            'weighted_average': weighted_average,
            'date': datetime.utcnow()
        }

        # Save to database
        save_rating(rating_data)
        return rating_data

    def process_csv(self, csv_path: str) -> list:
        """
        Process a CSV file containing retailer data.
        CSV should have columns: retailer_name, ios_url, android_url
        """
        try:
            df = pd.read_csv(csv_path)
            required_columns = ['retailer_name', 'ios_url', 'android_url']
            
            if not all(col in df.columns for col in required_columns):
                logger.error(f"CSV must contain columns: {required_columns}")
                return []

            results = []
            for _, row in df.iterrows():
                try:
                    result = self.process_retailer(
                        row['retailer_name'],
                        row['ios_url'],
                        row['android_url']
                    )
                    if result:
                        results.append(result)
                except Exception as e:
                    logger.error(f"Error processing retailer {row['retailer_name']}: {str(e)}")
                    continue

            return results

        except Exception as e:
            logger.error(f"Error reading CSV file: {str(e)}")
            return []

def main():
    processor = RetailerRatings()
    results = processor.process_csv('test_retailers.csv')
    
    # Print results in a formatted table
    print("\nRetailer App Ratings Summary:")
    print("-" * 80)
    print(f"{'Retailer':<15} {'iOS Score':<10} {'iOS Reviews':<12} {'Android Score':<12} {'Android Reviews':<15} {'Weighted Avg':<12}")
    print("-" * 80)
    
    for result in results:
        print(f"{result['retailer_name']:<15} "
              f"{result['ios_score']:<10.2f} "
              f"{result['ios_reviews']:<12} "
              f"{result['android_score']:<12.2f} "
              f"{result['android_reviews']:<15} "
              f"{result['weighted_average']:<12.2f}")

if __name__ == "__main__":
    main() 