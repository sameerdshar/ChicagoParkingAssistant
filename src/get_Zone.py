'''Scrape the city website to get the cleaning zones based on GPS location.''''''
Create Polygons.
'''

from shapely.geometry import MultiPolygon, Point, Polygon
import pandas as pd
import ast
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Example: create MultiPolygon from your list of coordinates
# Suppose you have a list of polygons, each as a list of (lon, lat) tuples

def create_multipolygons(coordinates):
    '''
    Create a MultiPolygon from a list of coordinates.
    :param coordinates: A list of coordinates where each coordinate is a list of (lon, lat) tuples.
    :return: A MultiPolygon object.'''
    
    logging.info("Creating MultiPolygon from coordinates.")
    if not coordinates or not isinstance(coordinates, pd.Series):
        logging.error("Invalid coordinates input.")
        return None
    
    try:
        polygons = coordinates.apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x).tolist()
    except Exception as e:
        logging.error(f"Error parsing coordinates: {e}")
        return None
    try:
        polygons = [Polygon(polygon) for polygon in polygons if isinstance(polygon, list) and len(polygon) > 0]
        if not polygons:
            logging.error("No valid polygons found in the coordinates.")
            return None
    except Exception as e:
        logging.error(f"Error creating polygons: {e}")
        return None

    try:
        multi_poly = MultiPolygon(polygons)
    except Exception as e:
        logging.error(f"Error creating MultiPolygon: {e}")
        return None

    return multi_poly

def get_zone(lat, long):
    """
    Check if a point is within any polygon in the MultiPolygon.
    :param point: A tuple (lon, lat) representing the point.
    :return: Ward number if the point is within any polygon, "Not in anyWard" otherwise.
    """
    logging.info(f"Checking zone for coordinates: ({lat}, {long})")
    if not isinstance(lat, (int, float)) or not isinstance(long, (int, float)):
        logging.error("Invalid latitude or longitude values.")
        return "Invalid coordinates"
    # Create a Point object from the coordinates
    logging.info("Creating Point object.")
    
    if lat < -90 or lat > 90 or long < -180 or long > 180:
        logging.error("Latitude or longitude out of bounds.")
        return "Coordinates out of bounds"
    
    logging.info("Creating Point object with valid coordinates.")   
    
    try:
        point = Point(lat, long)
    except Exception as e:
        logging.error(f"Error creating Point object: {e}")
        return "Error creating point"
    logging.info("Reading zone data from CSV file.")
    
    # Read the CSV file containing zone data
    try:
        df = pd.read_csv("chicago_zones.csv")
    except FileNotFoundError:
        logging.error("chicago_zones.csv file not found.")
        return "Zone data file not found"
    except Exception as e:
        logging.error(f"Error reading zone data file: {e}")
        return "Error reading zone data file"
    
    logging.info("Creating MultiPolygon for each ward and precinct.")
    
    # Iterate through each ward and precinct to find the matching zone
    try:
        logging.info("Iterating through wards and precincts to find matching zone.")
        for ward in df.ward.unique():
            for precinct in df.precinct.unique():
                multipolygon = create_multipolygons(df[(df.ward == ward) & (df.precinct == precinct)].coordinates)
                if point.within(multipolygon):
                    return ward, precinct
    except Exception as e:
        logging.error(f"Error checking point within polygons: {e}")
        return "Error checking zone"
    
    return "Not in any ward."

def __main__():
    """
    Main function to execute the script.
    :return: None
    """
    ward, section = get_zone(-87.70651898131568, 41.922342780375264)
    print(f"Ward: {ward} and Section: {section}")

if __name__ == "__main__":
    __main__()