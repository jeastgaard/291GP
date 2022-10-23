import sqlite3
import authentication
import userInterface
import artistInterface

cursor = None
connection = None

def create_connection( path ):
    global connection, cursor

    connection = sqlite3.connect( path )
    cursor = connection.cursor()

def close_database():
    # Add some error checking here!!
    global connection
    connection.commit()
    connection.close()

if __name__ == '__main__':
    path = './auth.db'

    print( '''Welcome to the First Group Project's Song Player!\n
    Please be aware, we don't actually play any music....''' )
    create_connection( path )
    authenticated = False
    while not authenticated:
        authenticated = authentication.get_authentication(cursor, connection)

    close_database()
    print( 'Success')
