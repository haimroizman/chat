__author__ = 'Haim'
import MySQLdb
from configparser import ConfigParser, Error
import os
from log_manager import LogManager


class Repository:
    def __init__(self, section):
        self.chat_db_config = self.read_db_config(section)  # Open Database connection
        self.logger = LogManager("chatApp")

    # For general execution, just pass the query
    def execute_query(self, query, params):
        conn = MySQLdb.connect(self.chat_db_config['host'], self.chat_db_config['user'],
                               self.chat_db_config['password'], self.chat_db_config['database'])
        cursor = conn.cursor()
        try:
            # Execute the SQL command
            cursor.execute(query, params)
            # Commit your changes in the database
            conn.commit()
        except Error as error:
            conn.rollback()
            self.logger.exception_log(error)
        conn.close()

    # A function with a yield return builds a generator object
    def execute_select_generator(self, query):

        conn = MySQLdb.connect(self.chat_db_config['host'], self.chat_db_config['user'],
                               self.chat_db_config['password'], self.chat_db_config['database'])
        cursor = conn.cursor()
        try:
            cursor.execute(query)
            results = cursor.fetchall()
            for row in results:
                yield row
        except Exception.message, error:
            self.logger.error_log("Error: unable to fetch data")
        conn.close()

    """
        Read database configuration file and return a dictionary object
        param filename: name of the configuration file
        param section: section of database configuration
        return: a dictionary of database parameters
    """

    def read_db_config(self, section, filename='config.ini'):
        filename = os.path.join(os.getcwd(), 'DB', filename)
        # create parser and read ini configuration file
        parser = ConfigParser()
        parser.read(filename)

        # get section, default to mysql
        db = {}
        if parser.has_section(section):
            items = parser.items(section)
            for item in items:
                db[item[0]] = item[1]
        else:
            raise Exception('%s not found in the %s file' % (section, filename))

        return db


