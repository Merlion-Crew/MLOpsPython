""" This file is used to setup the logging configuration as a dictionary.
    This dictionary object passed in to the logger utility class to decide the format,
    handlers (console, file, etc.) and log levels.
"""
import time
import logging

class UTCFormatter(logging.Formatter):
    converter = time.gmtime

logging_config = {
    'version': 1,
    'formatters': {
        'utc': {
            '()': UTCFormatter,
            'format': '%(asctime)s %(module)s.%(funcName)s:%(lineno)d [%(levelname)s]- %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'utc',
            'stream': 'ext://sys.stdout'
        }
    },
    'loggers': {
        'basic': {
            'level': 'DEBUG',
            'handlers': ['console']
        }
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['console']
    }
}