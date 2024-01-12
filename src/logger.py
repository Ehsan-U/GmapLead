import logging


logging.basicConfig(level=logging.WARNING,  
    format='=> %(levelname)s - %(module)s - %(asctime)s - %(message)s',
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),  # Logs to the console
    ])

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  