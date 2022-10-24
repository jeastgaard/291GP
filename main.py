import sqlite3
import authentication
import userInterface
import artistInterface

cursor = None
connection = None

def create_connection( path ):
    global connection, cursor
    # <todo> Add some error checking here!!
    connection = sqlite3.connect( path )
    cursor = connection.cursor()

def close_database():
    # <todo> Add some error checking here!!
    global connection
    connection.commit()
    connection.close()

if __name__ == '__main__':
    db_path ='./project.db'
    authenticated = False;
    create_connection( db_path )

    auth_interface = authentication.authenticationInterface(cursor, connection)
    print( '''Welcome to the First Group Project's Song Player!\n
    Please be aware, we don't actually play any music....''' )

    while not authenticated:
        login_choice = input("Login (1) or Sign Up(2)? (Q) to quite\n")

        if login_choice.lower() == 'q':
            break
        elif login_choice == '1':
            auth_interface.get_authentication()
        elif login_choice == '2':
            auth_interface.create_new_user()
        else:
            print("Choice Unrecognized, please try again...\n")
    close_database()
    print('Success')
