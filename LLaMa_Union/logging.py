import logging

# Configure logging
logging.basicConfig(level=logging.INFO, filename='manager_bot.log',
                    format='%(asctime)s:%(levelname)s:%(message)s')

# Use logging instead of print
logging.info('Manager Bot started')
