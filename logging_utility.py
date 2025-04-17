import sys
from logging import Logger
from typing import ClassVar

from loguru import logger


class LoggingUtility:
    __logger: ClassVar[logger] = logger

    @classmethod
    @property
    def logger(cls) -> Logger:
        return cls.__logger


    @staticmethod
    def start_logging() -> logger:
        """

        :rtype: object
        """
        log_format: str = '{time} - {name} - {level} - {function} - {message}'
        LoggingUtility.__logger.remove()
        LoggingUtility.__logger.add('formatted_log.txt', format = log_format, rotation = '10 MB',
                                    retention = '5 days')
        # Add a handler that logs only DEBUG messages to stdout
        LoggingUtility.__logger.add(sys.stdout, level = "DEBUG",
                                    filter = lambda record: record["level"].name == "DEBUG")
        return LoggingUtility.__logger
