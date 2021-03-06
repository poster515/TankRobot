import sqlite3
import sys

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    Input:
        db_file: database file
    Returns:
        Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except:
        print("Couldn't connect to database file.")
        sys.exit()

    return conn

def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except:
        print("Error creating SQLite table, exiting.")
        sys.exit()

def sql_table_func():
    return """ CREATE TABLE IF NOT EXISTS users (
                                        user_name TEXT NOT NULL,
                                        ip_addr TEXT NOT NULL,
                                        can_drive TEXT NOT NULL DEFAULT "False",
                                        is_driving TEXT NOT NULL DEFAULT "False",
                                        can_drive_endtime INTEGER,
                                        drive_endtime INTEGER); """
