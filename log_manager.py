__author__ = 'Haim'

import os
import logging
import logging.config


class LogManager:
    def __init__(self, logger_key):
        logging.config.fileConfig(os.path.abspath(os.path.join(os.getcwd(), 'logging.conf')))
        self.logger = logging.getLogger(logger_key)

    def info_log(self, log_message):
        self.logger.info(log_message)

    def error_log(self, log_message):
        self.logger.error(log_message)

    def exception_log(self, log_message):
        self.logger.exception(log_message)

    def debug_log(self, log_message):
        self.logger.debug((log_message))