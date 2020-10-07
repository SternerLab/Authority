import mysql.connector
import configparser


config_file = '../configs/db_config.ini'


class SQLClient:
    def __init__(self):
        self.connection = self.get_connection()
        self.cursor = self.connection.cursor()
        
    def get_connection(self):
        config = configparser.ConfigParser()
        config.read(config_file)
        return mysql.connector.connect(
        user = 'root', 
        password = 'password', 
        host = 'localhost', #todo
        port = 3306,
        ssl_disabled = True)


    def connect_to_db(self, database):
        self.cursor.execute('CREATE DATABASE IF NOT EXISTS '+ database)
        self.cursor.execute('USE '+ database)


    def close_connection(self):
        self.connection.close()


    def execute(self, query):
        self.cursor.execute(query)


    def execute_all(self, queries):
        for query in queries:
            self.cursor.execute(query)


    def insert_row(self, query, value):
        self.cursor.execute(query, value)
        self.connection.commit()

    
    def execute_sql_file(self, filepath):
        fd = open(filepath, 'r')
        sqlFile = fd.read()
        fd.close()
        print(sqlFile)
        self.cursor.execute(sqlFile)
        self.connection.commit()


    def execute_and_fetch(self, query):
        self.cursor.execute(query)
        return list(self.cursor.fetchall())