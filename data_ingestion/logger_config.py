import logging
import os
from dotenv import load_dotenv

#Initialize env vars
load_dotenv()
level = os.getenv('log_code')
logger_code = getattr(logging, level)

def initialize_log_config():
    logging.basicConfig(
        level=logger_code, 
        format= '%(asctime)s | %(levelname)s | %(name)s -> %(message)s'
        )
    
def get_logger(name):
    return logging.getLogger(name)
