import sqlite3
from sqlite3 import Error


class DbContext:
    sql_create_users_table = 'CREATE TABLE IF NOT EXISTS Users (username TEXT PRIMARY KEY, password TEXT NOT NULL,' \
                             ' first_name TEXT NOT NULL, last_name TEXT NOT NULL, email TEXT NOT NULL);'

    def __init__(self, database_name):
        self.databaseName = database_name
        self.connection = self.create_connection()
        self.create_table(DbContext.sql_create_users_table)

    def create_connection(self):
        try:
            conn = sqlite3.connect(self.databaseName, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
            return conn
        except Error as e:
            print(e)
        return None

    def insert_into_table(self, table_sql, values):
        cur = self.connection.cursor()
        cur.execute(table_sql, values)
        self.connection.commit()
        return

    def query_from_table(self, table_sql, values):
        cur = self.connection.cursor()
        cur.execute(table_sql, values)
        return cur.fetchall()

    def create_table(self, create_table_sql):
        try:
            c = self.connection.cursor()
            c.execute(create_table_sql)
        except Error as e:
            print(e)
