import logging

def initialize_log_config():
    logging.basicConfig(
        level=logging.INFO, 
        format= '%(asctime)s | %(levelname)s | %(name)s -> %(message)s'
        )
    
def get_logger(name):
    return logging.getLogger(name)