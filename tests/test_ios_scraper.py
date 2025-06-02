import pytest
from unittest.mock import patch, MagicMock
from scrapers.ios_scraper import IOSScraper

class TestIOSScraper:
    @pytest.fixture
    def scraper(self):
        return IOSScraper()

    def test_extract_app_id_valid_url(self, scraper):
        # Test with standard URL
        url = "https://apps.apple.com/us/app/walmart/id338137227"
        assert scraper.extract_app_id(url) == "338137227"
        
        # Test with URL containing app name
        url = "https://apps.apple.com/us/app/target-shopping/id297430070"
        assert scraper.extract_app_id(url) == "297430070"

    def test_extract_app_id_invalid_url(self, scraper):
        # Test with invalid URL
        url = "https://apps.apple.com/us/app/invalid"
        assert scraper.extract_app_id(url) is None
        
        # Test with non-Apple URL
        url = "https://play.google.com/store/apps/details?id=com.walmart.android"
        assert scraper.extract_app_id(url) is None

    @patch('requests.get')
    def test_get_app_ratings_success(self, mock_get, scraper):
        # Mock successful response
        mock_response = MagicMock()
        mock_response.text = """
        <div class="we-rating-count star-rating__count">
            <span class="we-rating-count__current">4.5</span>
            <span class="we-rating-count__total">(1,234)</span>
        </div>
        """
        mock_get.return_value = mock_response

        result = scraper.get_app_ratings("123456789")
        assert result is not None
        assert result['score'] == 4.5
        assert result['review_count'] == 1234

    @patch('requests.get')
    def test_get_app_ratings_network_error(self, mock_get, scraper):
        # Mock network error
        mock_get.side_effect = Exception("Network error")
        
        result = scraper.get_app_ratings("123456789")
        assert result is None

    @patch('requests.get')
    def test_get_app_ratings_invalid_html(self, mock_get, scraper):
        # Mock response with invalid HTML
        mock_response = MagicMock()
        mock_response.text = "<div>Invalid HTML</div>"
        mock_get.return_value = mock_response
        
        result = scraper.get_app_ratings("123456789")
        assert result is None

    @patch('requests.get')
    def test_scrape_retailer_app_success(self, mock_get, scraper):
        # Mock successful response
        mock_response = MagicMock()
        mock_response.text = """
        <div class="we-rating-count star-rating__count">
            <span class="we-rating-count__current">4.5</span>
            <span class="we-rating-count__total">(1,234)</span>
        </div>
        """
        mock_get.return_value = mock_response

        result = scraper.scrape_retailer_app(
            "Test Retailer",
            "https://apps.apple.com/us/app/test-app/id123456789"
        )
        
        assert result is not None
        assert result['retailer_name'] == "Test Retailer"
        assert result['app_id'] == "123456789"
        assert result['score'] == 4.5
        assert result['review_count'] == 1234

    def test_scrape_retailer_app_invalid_url(self, scraper):
        result = scraper.scrape_retailer_app(
            "Test Retailer",
            "https://invalid-url.com"
        )
        assert result is None 