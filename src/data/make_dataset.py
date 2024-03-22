import logging
from off_connector import OFFConnector, OFF_FIELD_CODE, OFF_FIELD_SELECTED_IMAGES, OFF_FIELDS_TO_EXPORT, OFF_FIELD_SELECTED_IMAGES_KEYS
from elefan_connector import ElefanConnector
from dotenv import find_dotenv, load_dotenv
import pandas as pd

logger = logging.getLogger(__name__)


def transform_products_facts(off_products_facts, source="off"):
    """
    Transform the list of products returned by the OFF API to a table ready to
    be loaded in a database
    """
    data = []
    for product_fact in off_products_facts:
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
        # source
        product_fact_data["source"] = source
        data.append(product_fact_data)
        # TODO : remove ';' from all values to avoid csv errors
        # TODO : remove white spaces
    return pd.DataFrame.from_records(data)


def main():
    """
    Runs data processing scripts to turn raw data from (../raw) into
    cleaned data ready to be analyzed (saved in ../processed).
    """
    logger = logging.getLogger(__name__)
    epicerie_connector = ElefanConnector(source="off")

    logger.info("Récuperation de la liste des codes barres de l'epicerie")
    epicerie_connector.extract_products_codes()
    epicerie_connector.transform_products_codes()
    logger.info(f"{len(epicerie_connector.products_codes)} codes filtrés à traiter")

    logger.info("Récuperation des données Open Food Facts disponibles pour cette liste")
    off_connector = OFFConnector(source="off")
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
