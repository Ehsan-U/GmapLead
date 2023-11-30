import logging

# Configure logging with a single statement using basicConfig
logging.basicConfig(level=logging.INFO,
    format='=> %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()])
logger = logging.getLogger("GoogleMaps")