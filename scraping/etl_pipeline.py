"""
ETL Pipeline for NCAA/USports Data Collection
- Extract: Web scraping using Beautiful Soup and Selenium
- Transform: Data cleaning and processing using Pandas
- Load: Database storage using SQLAlchemy
"""
import pandas as pd
from sqlalchemy import create_engine
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SportsETLPipeline:
    def __init__(self, db_url):
        """
        Initialize the ETL pipeline with database connection
        
        Args:
            db_url (str): Database connection URL for SQLAlchemy
        """
        self.db_url = db_url
        self.engine = create_engine(self.db_url)
        self.session = requests.Session()
        
    def extract_with_beautifulsoup(self, url):
        """
        Extract data from a URL using Beautiful Soup
        
        Args:
            url (str): URL to scrape
            
        Returns:
            BeautifulSoup: Parsed HTML object
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = self.session.get(url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            logger.info(f"Successfully extracted data from {url}")
            return soup
        except Exception as e:
            logger.error(f"Error extracting data from {url}: {str(e)}")
            return None
    
    def extract_with_selenium(self, url):
        """
        Extract data from a URL using Selenium (for dynamic content)
        
        Args:
            url (str): URL to scrape
            
        Returns:
            WebDriver: Selenium WebDriver instance with loaded page
        """
        try:
            # Configure Chrome options for headless operation
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(url)
            
            # Wait for page to load completely (adjust as needed)
            time.sleep(3)
            
            logger.info(f"Successfully loaded {url} with Selenium")
            return driver
        except Exception as e:
            logger.error(f"Error loading {url} with Selenium: {str(e)}")
            return None
    
    def transform_ncaa_data(self, raw_data):
        """
        Transform raw scraped data into structured format using Pandas
        
        Args:
            raw_data (list or dict): Raw data from scraping
            
        Returns:
            pandas.DataFrame: Clean, structured DataFrame
        """
        try:
            # Example transformation logic - adjust based on actual data structure
            if isinstance(raw_data, list):
                df = pd.DataFrame(raw_data)
            elif isinstance(raw_data, dict):
                df = pd.DataFrame([raw_data])
            else:
                raise ValueError("Raw data must be list or dict")
            
            # Clean and process the data
            df = self._clean_dataframe(df)
            
            logger.info(f"Successfully transformed {len(df)} records")
            return df
        except Exception as e:
            logger.error(f"Error transforming data: {str(e)}")
            return pd.DataFrame()
    
    def _clean_dataframe(self, df):
        """
        Internal method to clean the DataFrame
        
        Args:
            df (pandas.DataFrame): DataFrame to clean
            
        Returns:
            pandas.DataFrame: Cleaned DataFrame
        """
        # Remove duplicates
        df = df.drop_duplicates()
        
        # Handle missing values
        df = df.fillna('')
        
        # Convert data types as needed
        for col in df.columns:
            if df[col].dtype == 'object':
                # Convert strings to proper format
                df[col] = df[col].astype(str).str.strip()
        
        return df
    
    def load_data(self, df, table_name, if_exists='append'):
        """
        Load DataFrame into database table
        
        Args:
            df (pandas.DataFrame): DataFrame to load
            table_name (str): Name of the target table
            if_exists (str): What to do if table exists ('fail', 'replace', 'append')
        """
        try:
            df.to_sql(table_name, self.engine, if_exists=if_exists, index=False)
            logger.info(f"Successfully loaded {len(df)} records into {table_name}")
        except Exception as e:
            logger.error(f"Error loading data into {table_name}: {str(e)}")
    
    def run_etl(self, extractor_type, url, table_name):
        """
        Run the complete ETL process
        
        Args:
            extractor_type (str): Either 'beautifulsoup' or 'selenium'
            url (str): URL to extract data from
            table_name (str): Name of the table to load data into
            
        Returns:
            bool: Success status
        """
        try:
            logger.info(f"Starting ETL process for {url}")
            
            # Extract
            if extractor_type == 'beautifulsoup':
                raw_data = self.extract_with_beautifulsoup(url)
                if raw_data:
                    # Process the BeautifulSoup object to extract relevant data
                    # This is a simplified example - you'd customize this for your data
                    elements = raw_data.find_all(['tr', 'div', 'span'])  # Adjust selectors as needed
                    extracted_data = []
                    for element in elements:
                        # Extract relevant fields - customize based on your data structure
                        data = {
                            'html_content': str(element),
                            'text_content': element.get_text().strip(),
                            'tag': element.name
                        }
                        extracted_data.append(data)
                    raw_data = extracted_data
            elif extractor_type == 'selenium':
                driver = self.extract_with_selenium(url)
                if driver:
                    # Extract data using Selenium - customize based on your data
                    elements = driver.find_elements(By.TAG_NAME, 'tr')  # Adjust selectors as needed
                    extracted_data = []
                    for element in elements:
                        data = {
                            'html_content': element.get_attribute('outerHTML'),
                            'text_content': element.text.strip(),
                            'tag': element.tag_name
                        }
                        extracted_data.append(data)
                    raw_data = extracted_data
                    driver.quit()
            else:
                raise ValueError("Extractor type must be 'beautifulsoup' or 'selenium'")
            
            if not raw_data:
                logger.error("No data extracted, stopping ETL process")
                return False
            
            # Transform
            df = self.transform_ncaa_data(raw_data)
            if df.empty:
                logger.error("No data to load after transformation")
                return False
            
            # Load
            self.load_data(df, table_name)
            
            logger.info("ETL process completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error in ETL process: {str(e)}")
            return False

# Example usage function
def run_ncaa_etl_pipeline():
    """
    Example function to run the NCAA data ETL pipeline
    """
    # Using SQLite as example - in production, use PostgreSQL
    db_url = "sqlite:///sports_data.db"
    pipeline = SportsETLPipeline(db_url)
    
    # Example URLs for NCAA data - replace with actual NCAA/USports URLs
    urls_to_scrape = [
        "https://www.ncaa.com/stats/basketball-men/d1",
        "https://www.ncaa.com/stats/football/fbs",
        # Add more URLs as needed
    ]
    
    success_count = 0
    for url in urls_to_scrape:
        success = pipeline.run_etl(
            extractor_type='beautifulsoup',
            url=url,
            table_name='ncaa_scraped_data'
        )
        if success:
            success_count += 1
    
    logger.info(f"Completed ETL for {success_count}/{len(urls_to_scrape)} URLs")
    return success_count == len(urls_to_scrape)

if __name__ == "__main__":
    run_ncaa_etl_pipeline()