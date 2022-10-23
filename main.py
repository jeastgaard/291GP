import sqlite3

cursor = None
connection = None

def create_connection( path ):
    global connection, cursor

    connection = sqlite3.connect( path )
    cursor = connection.cursor()

def close_database():
    global connection
    connection.commit()
    connection.close()

if __name__ == '__main__':
    path = './project.db'

    create_connection( path )
    close_database()
    print( 'Success')
