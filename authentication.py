import os
import hashlib

import main

cursor = None
connection = None


def hash_password(password):
    alg = hashlib.sha256()
    alg.update(password.encode('utf-8'))
    return alg.hexdigest()


class AuthenticationInterface:
    def __init__(self, crs, conn):
        global cursor, connection
        cursor, connection = crs, conn

    def create_new_user(self):
        # First we need to load in all the existing usernames.
        all_current_users, all_current_artists = self.load_all_names()
        # Define our Queries to add users to database.
        add_user_query = "INSERT INTO users VALUES (:uid, :name, :pwd)"
        new_artist_query = "INSERT INTO artists VALUES (:uid, :name, :nat, :pwd)"

        print("users:\n", all_current_users, "\nartists:", all_current_artists)

        while True:
            username = input("Please Enter A Username: ")

            if [usr for usr in all_current_users if username in usr]\
                    or [usr for usr in all_current_artists if username in usr]:
                print("\nSorry, that username has already been taken. Please try another one:")
            else:
                name = input("Username is available!\nWhat should we call you? (Name)\n")
                break

        while True:
            new_user_table = input("\n Hi " + name + '''\nWould you like to be a:
            1: a user
            2: an artist
            3: both
            Q: Cancel\n''')

            if new_user_table == '1':
                password = hash_password( input("Please enter a password:\n ") )
                cursor.execute(add_user_query, {'uid': username, 'name': name, 'pwd': password})
                connection.commit()
                # todo Add error catching here
                print("User has been created successfully!")
                break
            elif new_user_table == '2':
                nationality = input("Please Enter Your Nationality:\n")
                password = hash_password(input("Please enter a password:\n "))
                cursor.execute( new_artist_query, {'uid': username, 'name': name, 'nat': nationality, 'pwd': password})
                connection.commit()
                # todo Add error catching here
                print("User has been created successfully!")
                break
            elif new_user_table == '3':
                nationality = input("Please Enter Your Nationality:\n")
                password = hash_password(input("Please enter a password:\n "))
                cursor.execute(new_artist_query, {'uid': username, 'name': name, 'nat': nationality, 'pwd': password})
                connection.commit()
                cursor.execute(add_user_query, {'uid': username, 'name': name, 'pwd': password})
                connection.commit()
                # todo Add error catching here
                print("User has been created successfully!")
                break
            elif new_user_table.lower() == 'q':
                break
            else:
                os.system('cls')
                print("That was an incorrect choice. Please choose again.")
    def get_authentication(self):
        global cursor
        while True:
            user_name = input("\n\nPlease Enter Your Username: \n")
            user_password = input("Please Enter Your Password:\n")
            user_password = hash_password(user_password)
            cursor.execute('''
            SELECT * FROM users WHERE uid = :uname AND pwd = :pw;''', {'uname': user_name, 'pw': user_password}, )
            users = cursor.fetchall()
            cursor.execute('''
            SELECT * FROM artists WHERE aid = :uname AND pwd = :pw;''', {'uname': user_name, 'pw': user_password}, )
            artists = cursor.fetchall()
            if len(users) != 1 and len(artists) != 1:
                print("User could not be authenticated.")
                return [], []
            else:
                return users, artists


    def check_access( self, user_name ):
        # Get the users interface access after they have been authenticated.
        cursor.execute("SELECT uid FROM users where uid = :username;", {'username': user_name})
        user = cursor.fetchone()
        print("User:", user)
        cursor.execute("SELECT aid FROM artists where aid = :username", {'username':user_name})
        artist = cursor.fetchone()
        print("Arists:", artist)
        if user is not None :
            if artist is not None:
                #We are an artist and user
                print("We are an artist and user")
            #We are a user
            print("We are a user")
        elif artist is not None:
            # We are an artist
            print("We are an artist")
        else:
            print("User authenticated but no account was found.")

    def load_all_names(self):
        global cursor
        cursor.execute('''
        SELECT uid FROM users;''')
        users = cursor.fetchall()
        cursor.execute('''
        SELECT aid FROM artists;''')
        artists = cursor.fetchall()
        return users, artists