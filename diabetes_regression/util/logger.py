from logging import Formatter, getLogger, DEBUG, INFO, StreamHandler
import logging.config
from opencensus.ext.azure.log_exporter import AzureLogHandler

import os
from util.logging_config import logging_config

def setup(log_to_local_only: bool = False):
    logging.config.dictConfig(logging_config)
    logger = getLogger()
    
    if not log_to_local_only:
        azure_log_handler = AzureLogHandler(
            instrumentation_key=os.environ.get("APPINSIGHTS_INSTRUMENTATION_KEY"),
            storage_path='mllogs'
        )
        azure_log_handler.setLevel(INFO)
        logger.addHandler(azure_log_handler)

if __name__ == "__main__":
    setup()
