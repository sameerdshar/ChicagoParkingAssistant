'''
This file gives the code for triangulating the vehicle in real time.

'''

import geocoder
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# import objc
# from Foundation import NSObject, NSLog, NSRunLoop, NSDate
# from CoreLocation import CLLocationManager, kCLAuthorizationStatusAuthorizedAlways

# class LocationManagerDelegate(NSObject):
#     '''Delegate class to handle location updates and errors.'''

#     def init(self):
#         '''Initialize the delegate and set up properties.'''
#         logging.info("Initializing LocationManagerDelegate.")
#         self = objc.super(LocationManagerDelegate, self).init()
#         self.has_location = False
#         self.latitude = None
#         self.longitude = None
#         return self

#     def locationManager_didUpdateLocations_(self, manager, locations):
#         '''Handle location updates.'''
#         logging.info("Location updated.")
#         location = locations[-1]
#         coord = location.coordinate()
#         self.latitude = coord.latitude
#         self.longitude = coord.longitude
#         logging.info(f"Latitude: {coord.latitude}, Longitude: {coord.longitude}")
#         self.has_location = True
#         manager.stopUpdatingLocation()

#     def locationManager_didFailWithError_(self, manager, error):
#         logging.error(f"Failed to get location: {error}")
#         # manager.stopUpdatingLocation()
#         self.has_location = False

def get_location():
    logging.info("Starting location retrieval process.")
    # # Create a CLLocationManager instance
    # logging.info("Creating CLLocationManager instance.")

    # # Initialize the location manager and delegate
    # logging.info("Initializing CLLocationManager and LocationManagerDelegate.")

    # logging.info("Setting up CLLocationManager and delegate.")
    # manager = CLLocationManager.alloc().init()
    # delegate = LocationManagerDelegate.alloc().init()
    # manager.setDelegate_(delegate)

    # # Request permission (if your app is configured)
    # logging.info("Requesting location authorization.")
    # if manager.authorizationStatus() != kCLAuthorizationStatusAuthorizedAlways:
    #     manager.requestAlwaysAuthorization()
    #     # For location updates while in use, use:
    #     # manager.requestWhenInUseAuthorization()
    #     # Note: Always request authorization only if your app needs it.
    # else:
    #     logging.info("Location authorization already granted.")

    # # Start updating location
    # logging.info("Starting location updates.")
    # manager.startUpdatingLocation()

    # # Wait until we get a location or fail
    # while not delegate.has_location:
    #     NSRunLoop.currentRunLoop().runUntilDate_(NSDate.dateWithTimeIntervalSinceNow_(0.1))
    
    logging.info("Fetching location using IP.")
    g = geocoder.ip('me')
    if g.ok:
        latitude, longitude = g.latlng
        logging.info(f"Location fetched successfully: Latitude={latitude}, Longitude={longitude}")

    else:
        logging.error("Failed to fetch location.")
        latitude, longitude = None, None

    return {
        'latitude': latitude,
        'longitude': longitude
    }


if __name__ == "__main__":
    result = get_location()
    print(result)