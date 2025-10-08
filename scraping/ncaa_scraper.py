"""
NCAA Data Scraper
Specialized scraper for NCAA/USports data using Beautiful Soup and Selenium
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NCAAScraper:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session.headers.update(self.headers)
    
    def scrape_ncaa_basic_data(self, url):
        """
        Scrape basic NCAA data using Beautiful Soup
        
        Args:
            url (str): URL to scrape
            
        Returns:
            list: List of dictionaries containing scraped data
        """
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Example: Find table rows containing player/team data
            # Adjust selectors based on the specific NCAA page structure
            data_rows = soup.find_all('tr')  # General selector - customize as needed
            
            scraped_data = []
            for row in data_rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) > 0:
                    row_data = {}
                    for i, cell in enumerate(cells):
                        # Example: Extract player stats, team names, etc.
                        key = f"column_{i}"
                        value = cell.get_text(strip=True)
                        row_data[key] = value
                    scraped_data.append(row_data)
            
            logger.info(f"Scraped {len(scraped_data)} records from {url}")
            return scraped_data
            
        except Exception as e:
            logger.error(f"Error scraping with Beautiful Soup from {url}: {str(e)}")
            return []
    
    def scrape_ncaa_dynamic_data(self, url):
        """
        Scrape dynamic NCAA data using Selenium (for JavaScript-heavy pages)
        
        Args:
            url (str): URL to scrape
            
        Returns:
            list: List of dictionaries containing scraped data
        """
        driver = None
        try:
            # Configure Chrome options
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(url)
            
            # Wait for dynamic content to load
            try:
                # Wait for table or data elements to load - customize selectors as needed
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "table"))
                )
            except:
                # If table doesn't load, wait for other content
                time.sleep(5)
            
            # Find data elements (tables, divs, etc.) - customize as needed
            elements = driver.find_elements(By.TAG_NAME, "tr")  # Example selector
            
            scraped_data = []
            for element in elements:
                # Extract relevant data from each element
                row_data = {
                    'html_content': element.get_attribute('outerHTML'),
                    'text_content': element.text.strip(),
                    'url': url
                }
                scraped_data.append(row_data)
            
            logger.info(f"Selenium scraped {len(scraped_data)} records from {url}")
            return scraped_data
            
        except Exception as e:
            logger.error(f"Error scraping with Selenium from {url}: {str(e)}")
            return []
        finally:
            if driver:
                driver.quit()
    
    def clean_and_structure_data(self, raw_data):
        """
        Clean and structure raw scraped data using Pandas
        
        Args:
            raw_data (list): List of dictionaries containing raw scraped data
            
        Returns:
            pandas.DataFrame: Clean structured DataFrame
        """
        if not raw_data:
            return pd.DataFrame()
        
        try:
            df = pd.DataFrame(raw_data)
            
            # Clean the data
            df = df.drop_duplicates()
            df = df.fillna('')
            
            # Standardize column names if needed
            df.columns = [col.strip().lower().replace(' ', '_').replace('-', '_') for col in df.columns]
            
            # Apply any specific data transformations needed for sports data
            # For example, converting string numbers to numeric types
            for col in df.columns:
                if df[col].dtype == 'object':
                    # Attempt to convert to numeric where possible
                    df[col] = df[col].apply(lambda x: pd.to_numeric(x, errors='ignore') if x != '' else x)
            
            logger.info(f"Structured {len(df)} records into DataFrame")
            return df
        except Exception as e:
            logger.error(f"Error structuring data: {str(e)}")
            return pd.DataFrame()
    
    def scrape_ncaa_basketball_stats(self, season="2023", category="scoring"):
        """
        Scrape NCAA basketball statistics
        
        Args:
            season (str): Season year to scrape
            category (str): Category of stats (scoring, rebounding, assists, etc.)
            
        Returns:
            pandas.DataFrame: DataFrame with basketball stats
        """
        base_url = f"https://www.ncaa.com/stats/basketball-men/d1/{category}/{season}"
        logger.info(f"Scraping NCAA basketball {category} stats for {season} season")
        
        # Try Beautiful Soup first
        data = self.scrape_ncaa_basic_data(base_url)
        
        # If Beautiful Soup doesn't get the data we need, fall back to Selenium
        if len(data) < 5:  # Adjust threshold as needed
            logger.info("Falling back to Selenium for dynamic content")
            data = self.scrape_ncaa_dynamic_data(base_url)
        
        df = self.clean_and_structure_data(data)
        return df
    
    def scrape_ncaa_football_stats(self, season="2023", category="passing"):
        """
        Scrape NCAA football statistics
        
        Args:
            season (str): Season year to scrape
            category (str): Category of stats (passing, rushing, receiving, etc.)
            
        Returns:
            pandas.DataFrame: DataFrame with football stats
        """
        base_url = f"https://www.ncaa.com/stats/football/fbs/{category}/{season}"
        logger.info(f"Scraping NCAA football {category} stats for {season} season")
        
        # Try Beautiful Soup first
        data = self.scrape_ncaa_basic_data(base_url)
        
        # If Beautiful Soup doesn't get the data we need, fall back to Selenium
        if len(data) < 5:  # Adjust threshold as needed
            logger.info("Falling back to Selenium for dynamic content")
            data = self.scrape_ncaa_dynamic_data(base_url)
        
        df = self.clean_and_structure_data(data)
        return df
    
    def scrape_multiple_categories(self, sport, season="2023"):
        """
        Scrape multiple categories of stats for a sport
        
        Args:
            sport (str): Sport type ('basketball' or 'football')
            season (str): Season year to scrape
            
        Returns:
            dict: Dictionary with category names as keys and DataFrames as values
        """
        results = {}
        
        if sport.lower() == 'basketball':
            categories = ['scoring', 'rebounding', 'assists', 'steals', 'blocks']
            for category in categories:
                df = self.scrape_ncaa_basketball_stats(season=season, category=category)
                results[category] = df
        elif sport.lower() == 'football':
            categories = ['passing', 'rushing', 'receiving', 'total-offense', 'scoring']
            for category in categories:
                df = self.scrape_ncaa_football_stats(season=season, category=category)
                results[category] = df
        else:
            logger.warning(f"Unsupported sport: {sport}")
            return {}
        
        return results

# Example usage
def run_ncaa_scraping():
    """
    Example function to run NCAA data scraping
    """
    scraper = NCAAScraper()
    
    # Example: Scrape basketball stats
    basketball_stats = scraper.scrape_multiple_categories('basketball', season='2023')
    
    # Example: Scrape football stats
    football_stats = scraper.scrape_multiple_categories('football', season='2023')
    
    # Combine and return results
    all_stats = {
        'basketball': basketball_stats,
        'football': football_stats
    }
    
    logger.info("NCAA data scraping completed")
    return all_stats

if __name__ == "__main__":
    run_ncaa_scraping()