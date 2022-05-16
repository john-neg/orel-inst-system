from flask.logging import create_logger
import logging.config

logging.config.fileConfig('logging.conf')

from app import create_app

app = create_app()
logger = create_logger(app)

app.run(debug=True)
