import sqlite3
import authentication
import userInterface
import artistInterface
from os import system, name


cursor = None
connection = None

def clear_screen():
    if name == 'nt':
        _ = system('cls')

        # for mac and linux(here, os.name is 'posix')
    else:
        _ = system('clear')

def create_connection(path):
    global connection, cursor
    # <todo> Add some error checking here!!
    connection = sqlite3.connect(path)
    cursor = connection.cursor()


def close_database():
    # <todo> Add some error checking here!!
    global connection
    connection.commit()
    connection.close()



if __name__ == '__main__':
    db_path = input("Please Enter the DB name you want to use:\n"
                    "Format: ./<name>.db\n")
    clear_screen()
    authenticated = False
    create_connection(db_path)

    auth_interface = authentication.AuthenticationInterface(cursor, connection)
    print('''Welcome to the First Group Project's Song Player!\n
    Please be aware, we don't actually play any music....''')


    # <todo> add check that aid cannot be converted to int.
    while not authenticated:
        login_choice = input("Login (1) or Sign Up(2)? (Q) to quite\n")

        if login_choice.lower() == 'q':
            break
        elif login_choice == '1':
            user_info, artist_info = auth_interface.get_authentication()

            # If both info's are populated then user needs to choose interface.
            if len(user_info) > 0 and len(artist_info) > 0:

                while True:
                    choice_of_interface = input(
                        "We see here that you are registered as a user and an artist.\nWould you like" +
                        " to proceed as a user(1) or artist(2)? Please enter your choice below: \n")
                    # Go into either artist interface or User interface based on the choice of user.
                    if choice_of_interface == '1':
                        # Launch the user interface here.
                        user_interface = userInterface.UserInterface(cursor, connection, user_info[0])
                        user_interface.launch_home_screen()
                        break
                    elif choice_of_interface == '2':
                        # Launch the artist interface here.
                        print("Debug:: You chose artist.")
                        artist_interface = artistInterface.ArtistInterface(cursor, connection, artist_info[0])
                        artist_interface.launch_home_screen()
                        break
                    else:
                        print("That was not a valid choice. Please try again!\n\n")
            elif len(user_info) > 0:
                # Launch the user here
                user_interface = userInterface.UserInterface( cursor, connection, user_info[0] )
                user_interface.launch_home_screen()
            elif len(artist_info) > 0:
                # Launch the artist interface here
                print("You are an artist")
                artist_interface = artistInterface.ArtistInterface( cursor, connection, artist_info[0] )
                artist_interface.launch_home_screen()

        elif login_choice == '2':
            auth_interface.create_new_user()
        else:
            print("Choice Unrecognized, please try again...\n")
    close_database()
    print('Success')

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


