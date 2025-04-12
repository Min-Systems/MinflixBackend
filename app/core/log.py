import logging

# Configure logging
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'  # Log format
)


# Get the logger for SQLModel and set its level to WARNING
sqlmodel_logger = logging.getLogger('sqlmodel')
sqlmodel_logger.setLevel(logging.WARNING)