import logging
from logging.handlers import RotatingFileHandler
import sys
import os
import platform

# Create a custom logger
logger = logging.getLogger("my_app")

# Set the level of this logger.
logger.setLevel(logging.DEBUG)

# Create handlers
console_handler = logging.StreamHandler()

# Determine log file location based on platform
if platform.system() in ('Windows', 'Darwin'):  # Windows or macOS
    # Use a logs directory in the current working directory for development
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'logs')
    # Create logs directory if it doesn't exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_file = os.path.join(log_dir, 'visualizer.log')
else:  # Linux (Raspberry Pi)
    log_dir = '/home/Piano-LED-Visualizer'
    # Create directory if it doesn't exist
    if not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir)
        except PermissionError:
            # Fallback to a location we can write to
            log_dir = os.path.expanduser('~')
    log_file = os.path.join(log_dir, 'visualizer.log')

# Create the file handler with the determined log file path
try:
    file_handler = RotatingFileHandler(log_file, maxBytes=500000, backupCount=10)
    file_handler_created = True
except (PermissionError, FileNotFoundError) as e:
    logger.warning(f"Couldn't create log file at {log_file}: {str(e)}")
    file_handler_created = False

# Set the level for handlers
console_handler.setLevel(logging.DEBUG)
if file_handler_created:
    file_handler.setLevel(logging.DEBUG)

# Create formatters and add it to handlers
formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s',
                              datefmt='%Y-%m-%d %H:%M:%S')
console_handler.setFormatter(formatter)
if file_handler_created:
    file_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(console_handler)
if file_handler_created:
    logger.addHandler(file_handler)


# Custom exception handler to log unhandled exceptions
def log_unhandled_exception(exc_type, exc_value, exc_traceback):
    logger.error("Unhandled Exception: ", exc_info=(exc_type, exc_value, exc_traceback))


# Set the custom exception handler
sys.excepthook = log_unhandled_exception
