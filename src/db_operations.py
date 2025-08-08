import sqlalchemy as sa
import yaml
import os
from time import sleep
import pandas as pd
from urllib.parse import quote_plus


def load_config(path: str) -> dict:
    """
    Load configuration from a YAML file.
    :param path: Path to the YAML configuration file
    :return: Dictionary containing configuration parameters
    """
    with open(path, "r") as file:
        config = yaml.safe_load(file)
    return config


def get_engine():
    """
    Establish a connection to the PostgreSQL database.
    :return: psycopg2 connection object
    """
    config = load_config(
        os.path.join(os.path.dirname(__file__), "..", "config", "config.yml")
    )
    db_config = config["database"]

    db_config = config["database"]
    user = db_config["DB_USER"]
    password = quote_plus(db_config["DB_PASSWORD"])
    host = db_config["DB_HOST"]
    port = db_config["DB_PORT"]
    db_name = db_config["DB_NAME"]

    engine = sa.create_engine(f"postgresql://{user}:{password}@{host}:{port}/{db_name}")
    return engine


def create_table(table_name: str, data: pd.DataFrame) -> None:
    """
    Create a table in the database.
    :param table_name: Name of the table to create
    :param data: Pandas dataframe to be inserted into the table
    :return: None
    """
    engine = get_engine()
    data.to_sql(table_name, con=engine, schema="CPA", if_exists="replace", index=False)
