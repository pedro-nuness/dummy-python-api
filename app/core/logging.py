import logging
import sys
from logging.handlers import RotatingFileHandler

LOG_FILE = "app.log"

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

file_handler = RotatingFileHandler(LOG_FILE, maxBytes=2*1024*1024, backupCount=5)
file_handler.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

logging.basicConfig(level=logging.INFO, handlers=[console_handler, file_handler])

logger = logging.getLogger("api")
logger.setLevel(logging.INFO)
