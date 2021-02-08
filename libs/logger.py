import logging
from logging import handlers

LOG_PATH = "mttSshServer.log"


class LogOperation:
    """
    Logger Class
    """

    def __init__(self, log_path=None, log_level=None):
        """
        First initialization
        """
        l_path = LOG_PATH
        if log_path is not None:
            l_path = log_path
        l_level = logging.INFO
        if log_level is not None:
            l_level = log_level
        self.__LOGGER = logging.getLogger(__name__)
        self.__LOGGER.setLevel(l_level)
        handler = logging.handlers.RotatingFileHandler(
            l_path, maxBytes=20 * 1024 * 1024, backupCount=5)
        handler.setLevel(l_level)
        formatter = logging.Formatter(
            '%(asctime)s.%(msecs)03d [%(process)s] %(levelname)s: '
            '%(message)s', "%m/%d/%Y %H:%M:%S")
        handler.setFormatter(formatter)
        if self.__LOGGER.hasHandlers():
            self.__LOGGER.handlers.clear()
        self.__LOGGER.addHandler(handler)

    def log_info(self, in_message) -> None:
        """
        Normal logger
        :param in_message: Log message
        :return: None
        """
        self.__LOGGER.info(in_message)

    def log_debug(self, in_message) -> None:
        """
        Debug Logger
        :param in_message: Log message
        :return: None
        """
        self.__LOGGER.debug(in_message)

    def log_warning(self, in_message) -> None:
        """
        Warning logger
        :param in_message: Warning log message
        :return: None
        """
        self.__LOGGER.warning(in_message)

    def log_error(self, in_message) -> None:
        """
        Error logger
        :param in_message: Error log message
        :return: None
        """
        self.__LOGGER.error(in_message, exc_info=True)
