import logging

# Basic logging configuration for the entire app
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    handlers=[
        logging.StreamHandler(),  # Logs to the console
    ]
)

# Log that the package is initialized
logging.info("common package initialized")

