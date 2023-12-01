import logging

# Configure logging with a single statement using basicConfig
logging.basicConfig(level=logging.DEBUG,
    format='=> %(levelname)s - %(module)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Logs to the console
        logging.FileHandler('logs/logs.log')  # Logs to a file named 'googlemaps.log'
    ])
logger = logging.getLogger("GoogleMaps")