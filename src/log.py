import logging
from datetime import datetime

log_file = f'log/{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.log'

# Create a logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)  # Set the logger to handle all levels (DEBUG and above)

# File handler (DEBUG level and above)
file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setLevel(logging.DEBUG)  # File handler will log DEBUG and above

# Console handler (INFO level and above)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)  # Console handler will log INFO and above

# Formatter
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', '%Y-%m-%d %H:%M:%S')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)