
'''
Hit the Chicago Data Portal API and fetch the cleaning schedule for zones.
'''

import pandas as pd
from sodapy import Socrata
import json
import ast
from datetime import date
import logging
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def safe_int_list(lst):
    '''
    Safely convert a list of strings to a list of integers, ignoring non-integer values
    :param lst: A list of strings.
    :return: A list of integers.
    '''
    return [int(i.strip()) for i in lst if i.strip().isdigit()]

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
            results = client.get(dataset_identifier, order="ward", offset=offset, limit=1000)
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

    normalized_df = pd.json_normalize(df['the_geom'])
    df = pd.concat([df.drop(['the_geom'], axis=1), normalized_df], axis=1)

    while len(df.coordinates[0]) == 1:
        df['coordinates'] = df['coordinates'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
        df = df.explode('coordinates').reset_index(drop=True)

    df['coordinates'] = df['coordinates'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

    df.to_csv("cleaning_schedule.csv", index=False)
    logging.info("Data retrieval complete. Data saved to 'cleaning_schedule.csv'.")
    # Print the total number of records retrieved

    logging.info(f"Total records retrieved: {len(df)}")

def get_cleaning_schedule(ward, section):
    """
    Fetch the street cleaning schedule for the current year.
    :return: DataFrame containing the street cleaning schedule.
    """
    try:
        df = pd.read_csv("cleaning_schedule.csv")
        logging.info("Cleaning schedule loaded from 'cleaning_schedule.csv'.")
 
    except FileNotFoundError:
        logging.error("Cleaning schedule file not found. Please run the data fetching script first.")
        return None

    concatenated_ward_section = f"{ward}{section}"
    logging.info(f"Fetching cleaning schedule for Ward: {ward}, Section: {section} (Concatenated: {concatenated_ward_section})")
    filtered_df = df[df.ward_section == concatenated_ward_section]

    print(df[df.ward_section == concatenated_ward_section])
    if filtered_df.empty:
        logging.warning(f"No cleaning schedule found for Ward: {ward}, Section: {section}.")
        return None
    logging.info(f"Found {len(filtered_df)} records for Ward: {ward}, Section: {section}.")
    month = dt.now().strftime("%B")
    next_month = (dt.now() + relativedelta(months=1)).strftime("%B")
    return filtered_df[['ward', 'section', month.lower(), next_month.lower()]]


def __main__():
    """
    Main function to execute the script.
    :return: None
    """
    get_cleaning_schedule_from_api()
if __name__ == "__main__":
    __main__()