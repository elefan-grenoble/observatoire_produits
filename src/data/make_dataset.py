import logging
from off_connector import OFFConnector
from elefan_connector import ElefanConnector
from dotenv import find_dotenv, load_dotenv
import pandas as pd

logger = logging.getLogger(__name__)


def transform_products_facts(off_products_facts):
    """
    Transform the  list of products returned by the OFF API to a table ready to
    be loaded in a database
    """
    data = []
    for product_fact in off_products_facts:
        try:
            image = product_fact["product"]["selected_images"]["front"]["display"]["fr"]
        except Exception:
            image = None
        data.append(
            {
                "code": product_fact["code"],
                "product_name": product_fact["product"].get("product_name", ""),
                "quantity": product_fact["product"].get("quantity", ""),
                "categories": product_fact["product"].get("categories", ""),
                "labels": product_fact["product"].get("labels", ""),
                "brands": product_fact["product"].get("brands", ""),
                "origins": product_fact["product"].get("origins", ""),
                "packaging": product_fact["product"].get("packaging", ""),
                "nutriscore_grade": product_fact["product"].get("nutriscore_grade", ""),
                "ecoscore_grade": product_fact["product"].get("ecoscore_grade", ""),
                "nova_group": product_fact["product"].get("nova_group", ""),
                "image": image,
            }
        )

        # TODO : remove ';' from all values to avoid csv errors
        # TODO : remove white spaces
    return pd.DataFrame.from_records(data)


def main():
    """
    Runs data processing scripts to turn raw data from (../raw) into
    cleaned data ready to be analyzed (saved in ../processed).
    """
    logger = logging.getLogger(__name__)
    epicerie_connector = ElefanConnector()

    logger.info("Récuperation de la liste des codes barres de l epicerie")
    epicerie_connector.extract_products_codes()
    epicerie_connector.transform_products_codes()

    logger.info("Récuperation des données Open Food Facts disponibles pour cette liste")
    off_connector = OFFConnector()
    off_connector.get_products_facts(epicerie_connector.products_codes)

    logger.info("Transformation des données Open Food Facts")
    products_facts = transform_products_facts(off_connector.products_facts)

    logger.info("Sauvegarde des données Open Food Facts")
    epicerie_connector.load_products_facts(products_facts)


if __name__ == "__main__":
    log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    main()
