import os

import dotenv
from epicerie_connector import EpicerieConnector

project_dir = os.path.join(os.path.dirname(__file__), os.pardir)
dotenv_path = os.path.join(project_dir, ".env")
dotenv.load_dotenv(dotenv_path)


class ElefanConnector(EpicerieConnector):
    def __init__(self) -> None:
        super().__init__()
        self.famille_code_food = [
            1,  # fruits & légumes
            2,  # épicerie salée
            3,  # épicerie sucrée
            4,  # boissons
            5,  # pains & pâtisseries
            11,  # viandes
            12,  # produits laitiers
            13,  # plats préparés
            14,  # poissons
            51,  # surgelés
        ]

    def filter_products(self):
        """
        epicerie-specific filtering rules:
        - exclude products with a code starting with "2" (usually custom barcodes)
        - the product status must be "ACTIF"
        - for now, only handle "food" products
        """
        self.products = [p for p in self.products if not p["code"].startswith("2")]
        self.products = [p for p in self.products if p["status"] == "ACTIF"]
        self.products = [
            p
            for p in self.products
            if p["famille"]["code"] in self.famille_code_food
        ]

    def extract_products_code_list(self):
        self.products_code_list = [p["code"] for p in self.products]

    def load_products_facts(self, products_facts):
        self.products_facts = products_facts
        self.products_facts.to_csv("products_facts.csv", sep=";", index=False)
        engine = self._db_connect()

        if len(self.products_facts):
            self.products_facts.to_sql("ARTICLE_FACTS", engine, if_exists="replace")
