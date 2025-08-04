'''
 Code to orchestrate the app. Empty for now.

Application Description:

Feature 1:
1. Get GPS location of the vehicle.
2. Get the city zone in which the vehicle is located.
3. Get the street cleaning schedule for that zone.
4. Return the street cleaning schedule.
5. Notify the user if the vehicle is parked in a street cleaning zone.
6. Notify the user if the vehicle is parked in a no parking zone.

Feature 2:
1. Get GPS location of the vehicle.
2. Get the GPS location of the parking spots.
3. Calculate the distance between the vehicle and each parking spot.
4. Sort the parking spots by distance.
5. Return the closest parking spot.
'''

from .get_GPS_location import get_location
from .get_Zone import get_zone
import logging
from .get_Cleaning_Schedule import get_cleaning_schedule

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def __main__():
    """
    Main function to execute the script.
    :return: None
    """
    # Get the GPS location of the vehicle
    location = get_location()
    latitude = location['latitude']
    longitude = location['longitude']
    
    # Get the zone based on GPS location
    zone = get_zone(latitude, longitude)
    
    if not isinstance(zone, dict):
        logging.error("Failed to retrieve zone information.")
        logging.error(zone)
        return
    # Print the results
    logging.info(f"Ward: {zone['ward']}, Section: {zone['section']}")

    # Get the street cleaning schedule for the zone
    logging.info(f"Fetching cleaning schedule for Ward: {zone['ward']}, Section: {zone['section']}")
    cleaning_schedule = get_cleaning_schedule(zone['ward'], zone['section'])
    if cleaning_schedule is not None:
        logging.info(f"Cleaning schedule for Ward: {zone['ward']}, Section: {zone['section']}:\n{cleaning_schedule}")
    else:
        logging.warning(f"No cleaning schedule found for Ward: {zone['ward']}, Section: {zone['precinct']}.")

if __name__ == "__main__":
    __main__()
    logging.info("Main function executed successfully.")
