import openfoodfacts
import logging
import requests
import time

logger = logging.getLogger(__name__)

# Select the facts you want to export
# You can find all the facts in this exemple
# https://world.openfoodfacts.net/api/v2/product/3017620429484


FACTS_TO_EXPORT = [
    "code",
    "product_name",
    "quantity",
    "categories",
    "brands",
    "labels",
    "origins",
    "packaging",
    "nutriscore_grade",
    "ecoscore_grade",
    "nova_group",
    "selected_images",
]


class OFFConnector:
    def __init__(self) -> None:
        self.products_facts = []
        self.api = openfoodfacts.API()

    def get_product_fact(self, barcode):
        try:
            product = self.api.product.get(barcode, fields=FACTS_TO_EXPORT)
            logger.info(f"Product found for url : https://world.openfoodfacts.org/api/v2/product/{barcode}")
        except requests.exceptions.HTTPError as e:
            logger.info(e)
            return None
        except requests.exceptions.ReadTimeout as e:
            logger.info(e)
            return None
        return product

    def get_products_facts(self, barcodes):
        """
        Reading the Open Food Facts API to fetch products facts
        Need to respect the API Constraint of a maximum of 100 requests
        per minute
        """
        start, end, step = 0, len(barcodes), 99
        number_of_requests = 0
        for i in range(start, end, step):
            x = i
            chunk = barcodes[x : x + step]
            for barcode in chunk:
                if number_of_requests == 99:
                    logger.info("Waiting 60 seconds...")
                    time.sleep(60)
                    number_of_requests = 0

                # A valid barcode is likely to have at least 10 digits
                if len(str(barcode)) >= 10:
                    product_fact = self.get_product_fact(barcode)
                    if product_fact:
                        self.products_facts.append(product_fact)
                    number_of_requests += 1
