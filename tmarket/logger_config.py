# logger_config.py
import logging
import os

# Basic configuration to log messages to a file
logging.basicConfig(filename=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'docs/tmarket.log'), 
                    level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def get_logger(module_name):
    """Return a logger instance for the module."""
    logger = logging.getLogger(module_name)
    return logger
