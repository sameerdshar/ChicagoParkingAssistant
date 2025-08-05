'''
Hit the Chicago Data Portal API and fetch the details of zones.
'''

import pandas as pd
from sodapy import Socrata
import json
import ast
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def get_zone_details():
    """
    Fetch zone details from the Chicago Data Portal and save to a CSV file.
    :return: None
    """
    # Initialize the Socrata client
    logging.info("Starting to fetch zone details from the Chicago Data Portal.")
    client = Socrata("data.cityofchicago.org", None)

    # Specify the dataset identifier (found in the URL of the dataset on the portal)
    # dataset_identifier = "p293-wvbd" 
    dataset_identifier = "6piy-vbxa"
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

    # Convert the list of dictionaries to a DataFrame for easier manipulation
    df = pd.DataFrame(all_results)
    normalized_df = pd.json_normalize(df['the_geom'])
    df = pd.concat([df.drop(['the_geom'], axis=1), normalized_df], axis=1)

    while len(df.coordinates[0]) == 1:
        df['coordinates'] = df['coordinates'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
        df = df.explode('coordinates').reset_index(drop=True)

    df['coordinates'] = df['coordinates'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
    df['ward'] = pd.to_numeric(df['ward'], errors='coerce').astype('Int64')
    df['precinct'] = pd.to_numeric(df['precinct'], errors='coerce').astype('Int64')
    df.to_csv("chicago_zones.csv", index=False)
    logging.info("Zone details saved to 'chicago_zones.csv'.")
    logging.info(f"Total records retrieved: {len(df)}")

def __main__():
    """
    Main function to execute the script.
    :return: None
    """
    get_zone_details()
if __name__ == "__main__":
    __main__()