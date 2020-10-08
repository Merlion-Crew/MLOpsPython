from logging import Formatter, getLogger, DEBUG, INFO, StreamHandler
import logging.config
from opencensus.ext.azure.log_exporter import AzureLogHandler

from ml_service.util.env_variables import Env
from ml_service.util.logging_config import logging_config


def setup_logging(log_to_local_only: bool = False, env: Env = None):
    """Log Utility method to setup python logging with necessary
       configuration to publish logs locally or to cloud

    Keyword Arguments:
        log_to_local_only (bool) -- Set to True if you want to publish logs to stream only.   (default: {False})
                                    False indicates logs will be published to Azure (AppInsights Service is used here)
        env (Env) -- an instance of Env class that loads & stores all environment variables. Used for UT (default: {None})
    """
    if env is None:
        env = Env()

    logging.config.dictConfig(logging_config)
    logger = getLogger()

    if not log_to_local_only:
    # Assumes the environment variable APPINSIGHTS_INSTRUMENTATION_KEY is already set
        azure_log_handler = AzureLogHandler(
            instrumentation_key=env.appinsights_instrumentation_key,
            storage_path='logs'
        )
        azure_log_handler.setLevel(INFO)
        logger.addHandler(azure_log_handler)

if __name__ == "__main__":
    setup_logging(True)
