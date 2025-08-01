
'''
Hit the Chicago Data Portal API and fetch the cleaning schedule for zones.
'''

import pandas as pd
from sodapy import Socrata
import json
import ast
from datetime import date
import logging

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
    dataset_identifier = "a2xx-z2ja"
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
    df['year'] = date.today().year
    df['dates_list'] = df['dates'].str.split(',').apply(
        lambda lst: [int(i.strip()) for i in lst if i.strip().isdigit()])
    df['dates_list'] = df['dates'].str.split(',').apply(safe_int_list)
    df['month_number'] = df['month_number'].astype('int64')
    df = df.explode('dates_list')

    df['date'] = pd.to_datetime({
        'year': df['year'],
        'month': df['month_number'],
        'day': df['dates_list']
        })

    df.to_csv("cleaning_schedule.csv", index=False)
    logging.info("Data retrieval complete. Data saved to 'cleaning_schedule.csv'.")
    # Print the total number of records retrieved

    logging.info(f"Total records retrieved: {len(df)}")

def __main__():
    """
    Main function to execute the script.
    :return: None
    """
    get_cleaning_schedule_from_api()
if __name__ == "__main__":
    __main__()