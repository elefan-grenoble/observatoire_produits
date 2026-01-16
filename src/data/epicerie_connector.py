import logging
import os
import sys

import requests
import sqlalchemy

logger = logging.getLogger(__name__)


class EpicerieConnector:
    def __init__(self) -> None:
        self.db_username = os.environ.get("DB_USERNAME")
        self.db_password = os.environ.get("DB_PASSWORD")
        self.db_host = os.environ.get("DB_HOST")
        self.db_name = os.environ.get("DB_NAME")
        self.api_url = os.environ.get("API_URL")

        self.products = None
        self.products_code_list = None

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

    def extract_products(self):
        """
        Step 1: Connect to the epicerie API and fetch all products
        """
        if self.api_url:
            try:
                response = requests.get(self.api_url)
                self.products = response.json()
            except requests.exceptions.HTTPError as e:
                logger.info(e)
                return None
        else:
            logging.error("Please provide a way to connect to your epicerie products")

    def filter_products(self):
        """
        Step 2 (optional): filter products according to epicerie-specific rules
        """
        pass

    def extract_products_code_list(self):
        """
        Step 3: extract product codes from filtered products
        """
        pass

    def filter_products_code_list(self):
        """
        Step 4: filter product codes
        - keep only EAN8 & EAN13 codes
        """
        self.products_code_list = [code for code in self.products_code_list if len(str(code)) in [8, 13]]
        if os.environ.get("DEBUG"):
            self.products_code_list = self.products_code_list[0:50]

    def get_products_code_list(self):
        self.extract_products()
        self.filter_products()
        self.extract_products_code_list()
        self.filter_products_code_list()

    def load_products_facts(self, products_facts):
        pass
