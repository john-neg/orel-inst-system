from flask.logging import create_logger
import logging.config

logging.config.fileConfig('logging.conf')

from app import create_app

app = create_app()
logger = create_logger(app)

logger.debug('debug message')
logger.info('info message')
logger.warning('warn message')
logger.error('error message')
logger.critical('critical message')

app.run(debug=True)
