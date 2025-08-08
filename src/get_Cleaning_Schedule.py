"""
Hit the Chicago Data Portal API and fetch the cleaning schedule for zones.
"""

import pandas as pd
from sodapy import Socrata
import json
import ast
from datetime import date
import logging
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta
from db_operations import create_table, get_engine

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def safe_int_list(lst):
    """
    Safely convert a list of strings to a list of integers, ignoring non-integer values
    :param lst: A list of strings.
    :return: A list of integers.
    """
    return [int(i.strip()) for i in lst if i.strip().isdigit()]


def extract_dates(row):
    dates = []
    year = date.today().year
    # Melt the DataFrame to long format
    months = [
        "april",
        "may",
        "june",
        "july",
        "august",
        "september",
        "october",
        "november",
    ]
    month_map = {month: i + 4 for i, month in enumerate(months)}
    for month in months:
        days_str = str(row[month])
        if days_str:
            try:
                days = [
                    int(day.strip())
                    for day in days_str.split(",")
                    if day.strip().isdigit()
                ]
                for day in days:
                    cleaning_date = dt(year, month_map[month], day).strftime("%Y-%m-%d")
                    dates.append(cleaning_date)
            except Exception:
                continue  # skip invalid entries
    return dates


def get_cleaning_schedule_from_api():
    """
    Fetch zone details from the Chicago Data Portal and save to a CSV file.
    :return: None
    """
    # Initialize the Socrata client
    logging.info("Starting to fetch cleaning schedule from the Chicago Data Portal.")
    client = Socrata("data.cityofchicago.org", None)
    # https://data.cityofchicago.org/api/v3/views/p293-wvbd/query.json

    # Specify the dataset identifier (found in the URL of the dataset on the portal)
    # dataset_identifier = "p293-wvbd"
    dataset_identifier = "utb4-q645"
    offset = 0
    all_results = []
    try:
        logging.info("Retrieving data from the API...")

        while True:
            results = client.get(
                dataset_identifier, order="ward", offset=offset, limit=1000
            )
            offset += 1000
            if not results:
                break
            all_results += results
    except Exception as e:
        logging.error(f"An error occurred while fetching data: {e}")
        return

    # Close the client session when finished
    client.close()
    logging.info("Data retrieval complete. Processing the results.")

    # # Convert the list of dictionaries to a DataFrame for easier manipulation
    df = pd.DataFrame(all_results)

    normalized_df = pd.json_normalize(df["the_geom"])
    df = pd.concat([df.drop(["the_geom"], axis=1), normalized_df], axis=1)

    while len(df.coordinates[0]) == 1:
        df["coordinates"] = (
            df["coordinates"]
            .apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
            .tolist()
        )
        df = df.explode("coordinates").reset_index(drop=True)

    df["coordinates"] = df["coordinates"].apply(json.dumps)

    df["date"] = df.apply(extract_dates, axis=1)
    df = df.explode("date").reset_index(drop=True)

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    create_table("cleaning_schedule", df)
    logging.info(
        "Data retrieval complete. Data saved to table 'cleaning_schedule' in the database."
    )
    # Print the total number of records retrieved

    logging.info(f"Total records retrieved: {len(df)}")


def get_cleaning_schedule(ward, section):
    """
    Fetch the street cleaning schedule for the current year.
    :return: DataFrame containing the street cleaning schedule.
    """
    date_today = date.today()
    end_date = date_today + relativedelta(months=1)

    query = f"""
    SELECT date FROM "CPA".cleaning_schedule
    WHERE ward_id = '{ward}' AND section_id = '{section}'
    AND date >= TO_TIMESTAMP('{date_today}', 'YYYY-MM-DD') AND date <= TO_TIMESTAMP('{end_date}', 'YYYY-MM-DD')
    ORDER BY date
    """

    engine = get_engine()
    try:
        with engine.connect() as connection:
            df = pd.read_sql(query, connection)
        if df.empty:
            logging.warning(
                f"No cleaning schedule found for Ward: {ward}, Section: {section}."
            )
            return None
        else:
            logging.info(
                f"Cleaning schedule found for Ward: {ward}, Section: {section}."
            )
            return df.date.tolist()
    except Exception as e:
        logging.error(f"An error occurred while fetching the cleaning schedule: {e}")
        return None


def __main__():
    """
    Main function to execute the script.
    :return: None
    """
    get_cleaning_schedule_from_api()
    # result = get_cleaning_schedule(48, 6)
    # print(result)


if __name__ == "__main__":
    __main__()
