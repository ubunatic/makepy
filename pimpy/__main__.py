import logging
from pimpy import mainlog
mainlog.setup_logging(use_structlog=True)
log = logging.getLogger(__name__)
log.warn("pimpy has no main ;)")
