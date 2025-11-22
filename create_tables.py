import os
import psycopg2
from sql_queries import create_table_queries, drop_table_queries

def create_database():
    """
    - Creates and connects to the sparkifydb
    - Returns the connection and cursor to sparkifydb
    """
    # Get database connection parameters from environment variables or use defaults
    db_host = os.getenv('DB_HOST', '127.0.0.1')
    db_port = os.getenv('DB_PORT', '5432')
    db_user = os.getenv('DB_USER', 'student')
    db_password = os.getenv('DB_PASSWORD', 'student')
    default_db = os.getenv('DEFAULT_DB', 'studentdb')
    target_db = os.getenv('DB_NAME', 'sparkifydb')
    
    # connect to default database
    conn = psycopg2.connect(
        host=db_host,
        port=db_port,
        dbname=default_db,
        user=db_user,
        password=db_password
    )
    conn.set_session(autocommit=True)
    cur = conn.cursor()
    
    # create sparkify database with UTF8 encoding
    cur.execute("DROP DATABASE IF EXISTS sparkifydb")
    cur.execute("CREATE DATABASE sparkifydb WITH ENCODING 'utf8' TEMPLATE template0")

    # close connection to default database
    conn.close()    
    
    # connect to sparkify database
    conn = psycopg2.connect(
        host=db_host,
        port=db_port,
        dbname=target_db,
        user=db_user,
        password=db_password
    )
    cur = conn.cursor()
    
    return cur, conn


def drop_tables(cur, conn):
    """
    Drops each table using the queries in `drop_table_queries` list.
    """
    for query in drop_table_queries:
        cur.execute(query)
        conn.commit()


def create_tables(cur, conn):
    """
    Creates each table using the queries in `create_table_queries` list. 
    """
    for query in create_table_queries:
        cur.execute(query)
        conn.commit()


def main():
    """
    - Drops (if exists) and Creates the sparkify database. 
    
    - Establishes connection with the sparkify database and gets
    cursor to it.  
    
    - Drops all the tables.  
    
    - Creates all tables needed. 
    
    - Finally, closes the connection. 
    """
    cur, conn = create_database()
    
    drop_tables(cur, conn)
    create_tables(cur, conn)

    conn.close()


if __name__ == "__main__":
    main()