import logging

# Set the basic configuration for the root logger
logging.basicConfig(level=logging.WARNING,  # Set higher level for root logger
    format='=> %(levelname)s - %(module)s - %(asctime)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Logs to the console
        logging.FileHandler('logs/logs.log')  # Logs to a file
    ])

# Get the logger for 'GoogleMaps' and set its level to DEBUG
logger = logging.getLogger("GoogleMaps")
logger.setLevel(logging.DEBUG)  # Set DEBUG level for GoogleMaps logger
