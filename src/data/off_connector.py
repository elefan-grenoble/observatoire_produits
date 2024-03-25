import openfoodfacts
import logging
import requests
import time

logger = logging.getLogger(__name__)

# Select the fields you want to export
# You can find all the fields in this exemple
# https://world.openfoodfacts.org/api/v2/product/3017620429484


OFF_FIELDS_TO_EXPORT = [
    "code",
    "product_name",
    "quantity",
    "categories",
    "brands",
    "labels",
    "origins",
    "packaging",
    "stores",
    "countries",
    "ingredients_text",
    "nutrition_data",
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
            product = self.api.product.get(barcode, fields=OFF_FIELDS_TO_EXPORT)
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
        for index, barcode in enumerate(barcodes):
            product_fact = self.get_product_fact(barcode)
            if product_fact:
                self.products_facts.append(product_fact)
            # Avoid too many calls to the API
            # 5 second sleep every 10 API calls
            if (index % 10) == 0:
                time.sleep(5)
