import logging
from rich.logging import RichHandler

FORMAT = "%(message)s"
logging.basicConfig(
    level='INFO', format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)
# log = logging.getLogger('rich')
# log.setLevel(logging.INFO) # Default level
