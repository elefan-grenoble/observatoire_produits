from epicerie_connector import EpicerieConnector
import os
import dotenv

project_dir = os.path.join(os.path.dirname(__file__), os.pardir)
dotenv_path = os.path.join(project_dir, ".env")
dotenv.load_dotenv(dotenv_path)


class ElefanConnector(EpicerieConnector):
    def __init__(self, source="off") -> None:
        super().__init__()
        self.source = source
        self.off_codes_to_exclude = [
            21,  # bebe (inclus nourriture)
            22,  # hygiène, beauté
            23,  # entretien, nettoyage
            24,  # cuisine
            25,  # santé
            31,  # journaux
            41,  # maison
            42,  # papeterie
            43,  # textile
            44,  # animalerie
            45,  # jardinerie
            90,  # jeux
        ]
        self.obf_codes_to_include = [
            21,  # bebe (inclus nourriture...)
            22,  # hygiène, beauté
            25,  # santé
        ]
        self.opf_codes_to_include = [
            24,  # cuisine
            31,  # journaux
            41,  # maison
            42,  # papeterie
            43,  # textile
            44,  # animalerie
            45,  # jardinerie
            90,  # jeux
        ]
        self.opff_codes_to_include = []

    def filter_products(self):
        """
        - product status must be "ACTIF"
        - filtering depending on famille code & source (off, obf, opf, opff)
        """
        self.products = [p for p in self.products if p["status"] == "ACTIF"]
        if self.source == "off":
            self.products = [p for p in self.products if p["famille"]["code"] not in self.off_codes_to_exclude]
        elif self.source == "obf":
            self.products = [p for p in self.products if p["famille"]["code"] in self.obf_codes_to_include]
        elif self.source == "opf":
            self.products = [p for p in self.products if p["famille"]["code"] in self.opf_codes_to_include]

    def extract_products_codes(self):
        self.extract_products()
        self.products_codes = [p["code"] for p in self.products]

    def load_products_facts(self, products_facts):
        self.products_facts = products_facts
        self.products_facts.to_csv("products_facts.csv", sep=";", index=False)
        engine = self._db_connect()

        if len(self.products_facts):
            self.products_facts.to_sql("ARTICLE_FACTS", engine, if_exists="replace")
