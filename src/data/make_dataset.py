import logging
from off_connector import OFFConnector
from elefan_connector import ElefanConnector
from dotenv import find_dotenv, load_dotenv

logger = logging.getLogger(__name__)


def main():
    """
    Runs data processing scripts to turn raw data from (../raw) into
    cleaned data ready to be analyzed (saved in ../processed).
    """
    logger = logging.getLogger(__name__)
    epicerie_connector = ElefanConnector()

    logger.info("Récuperation de la liste des codes barres de l'epicerie")
    epicerie_connector.get_products_code_list()
    logger.info(f"{len(epicerie_connector.products_codes)} codes filtrés à traiter")

    logger.info("Récuperation des données Open Food Facts disponibles pour cette liste")
    off_connector = OFFConnector()
    off_connector.get_products_facts(epicerie_connector.products_codes)

    logger.info("Transformation des données Open Food Facts")
    off_connector.transform_products_facts()

    logger.info("Sauvegarde des données Open Food Facts")
    epicerie_connector.load_products_facts(off_connector.products_facts_cleaned)


if __name__ == "__main__":
    log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    main()
