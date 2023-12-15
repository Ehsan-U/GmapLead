import logging
import os


log_directory = "logs"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

logging.basicConfig(level=logging.WARNING,  
    format='=> %(levelname)s - %(module)s - %(asctime)s - %(message)s',
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),  # Logs to the console
        logging.FileHandler('logs/logs.log')  # Logs to a file
    ])

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  