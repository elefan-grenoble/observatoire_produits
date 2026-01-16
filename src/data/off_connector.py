import logging
import time
import pandas as pd

import openfoodfacts
import requests

logger = logging.getLogger(__name__)

# Select the fields you want to export
# You can find all the fields in this exemple
# https://world.openfoodfacts.org/api/v2/product/3017620429484


APP_USER_AGENT = "elefan-grenoble/observatoire_produits"
OFF_FIELD_CODE = "code"
OFF_FIELD_SELECTED_IMAGES = "selected_images"
OFF_FIELDS_TO_EXPORT = [
    OFF_FIELD_CODE,
    "product_name",
    "quantity",
    "categories",
    "brands",
    "labels",
    "origins",
    "ingredients_text",
    "nutrition_data",
    "packaging",
    "nutriscore_grade",
    "ecoscore_grade",
    "nova_group",
    OFF_FIELD_SELECTED_IMAGES,
]

OFF_FIELD_SELECTED_IMAGES_KEYS = ["front", "ingredients", "nutrition", "packaging"]


class OFFConnector:
    def __init__(self) -> None:
        self.api = openfoodfacts.API(user_agent=APP_USER_AGENT)
        self.products_facts = []
        self.products_facts_cleaned = []

    def _get_product_fact(self, barcode):
        try:
            product = self.api.product.get(barcode, fields=OFF_FIELDS_TO_EXPORT)
            logger.info(
                f"Product found for url : https://world.openfoodfacts.org/api/v2/product/{barcode}"
            )
        except requests.exceptions.HTTPError as e:
            logger.info(e)
            return None
        except requests.exceptions.ReadTimeout as e:
            logger.info(e)
            return None
        return product

    def get_products_facts(self, epicerie_barcode_list):
        """
        Use the Open Food Facts API to fetch products facts
        Note: API constraint of max 100 requests per minute
        """
        for index, barcode in enumerate(epicerie_barcode_list):
            product_fact = self._get_product_fact(str(barcode))
            if product_fact:
                self.products_facts.append(product_fact)
            # Avoid too many calls to the API
            # 5 second sleep every 10 API calls
            if (index % 10) == 0:
                time.sleep(5)


    def transform_products_facts(self):
        """
        Transform the list of products returned by the OFF API to a table ready to
        be loaded in a database
        """
        data = []
        for product_fact in self.products_facts:
            product_fact_data = {}
            # code
            product_fact_data[OFF_FIELD_CODE] = product_fact[OFF_FIELD_CODE]
            # simple fields
            for field in [f for f in OFF_FIELDS_TO_EXPORT if f not in [OFF_FIELD_CODE, OFF_FIELD_SELECTED_IMAGES]]:
                product_fact_data[field] = product_fact["product"].get(field, "")
            # images
            for image_field in OFF_FIELD_SELECTED_IMAGES_KEYS:
                try:
                    product_fact_data[f"{OFF_FIELD_SELECTED_IMAGES}_{image_field}"] = product_fact["product"][OFF_FIELD_SELECTED_IMAGES][image_field]["display"]["fr"]
                except Exception:
                    product_fact_data[f"{OFF_FIELD_SELECTED_IMAGES}_{image_field}"] = None
            data.append(product_fact_data)
            # TODO : remove ';' from all values to avoid csv errors
            # TODO : remove white spaces
        self.products_facts_cleaned = pd.DataFrame.from_records(data)
