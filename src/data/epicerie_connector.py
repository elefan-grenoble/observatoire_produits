import sqlalchemy
import os
import requests
import logging
import sys

logger = logging.getLogger(__name__)


class EpicerieConnector:
    def __init__(self) -> None:
        self.db_username = os.environ.get("DB_USERNAME")
        self.db_password = os.environ.get("DB_PASSWORD")
        self.db_host = os.environ.get("DB_HOST")
        self.db_name = os.environ.get("DB_NAME")
        self.api_url = os.environ.get("API_URL")

        self.products_facts = None
        self.products = None
        self.products_codes = None

    def filter_products():
        pass

    def extract_products(self):
        if self.api_url:
            try:
                response = requests.get(self.api_url)
                self.products = response.json()
                self.filter_products()
            except requests.exceptions.HTTPError as e:
                logger.info(e)
                return None
        else:
            logging.error("Please provide a way to connect to your epicerie products")

    def extract_products_codes(self):
        pass

    def transform_products_codes(self):
        """
        keep only EAN8 & EAN13 codes
        """
        self.products_codes = [code for code in self.products_codes if len(str(code)) in [8, 13]]
        if os.environ.get("DEBUG"):
            self.products_codes = self.products_codes[0:50]

    def _db_connect(self):
        # Connect to a DB
        try:
            engine = sqlalchemy.create_engine(
                f"mysql+pymysql://{self.db_username}:{self.db_password}"
                f"@{self.db_host}/{self.db_name}?charset=utf8mb4"
            )
        except sqlalchemy.exc as e:
            print(f"Error connecting to MariaDB Platform: {e}")
            sys.exit(1)
        return engine
