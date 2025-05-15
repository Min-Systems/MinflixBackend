import logging
from app.core.log import sqlmodel_logger

def test_logging_configuration():
    root_logger = logging.getLogger()
    assert root_logger.level <= logging.INFO
    assert sqlmodel_logger.level == logging.WARNING