import sqlite3

class sqlite_client:
    def __init__(self, database):
        self.connection = self.get_connection(database)
        self.cursor = self.connection.cursor()
        

    def get_connection(self, database):
        return sqlite3.connect(database)


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