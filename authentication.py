import os
import hashlib

""" hash_password will encode the given string.
Intended to be used so that a users password
can be stored securely."""


def hash_password(password):
    alg = hashlib.sha256()
    alg.update(password.encode('utf-8'))
    return alg.hexdigest()


""" Class: AuthenticationInterface
This class will hold the cursor and connection so that users can be
authenticated within the database."""


class AuthenticationInterface:
    def __init__(self, crs, conn):
        # global cursor, connection
        self.cursor, self.connection = crs, conn

    """ creaate_new_user will prompt the user to create a new account.
    This will store the username and all other given information in the
    database depending if the user signs up as an artists or regular user."""
    def create_new_user(self):
        # global cursor, connection
        # First we need to load in all the existing usernames.
        all_current_users, all_current_artists = self.load_all_names()
        # Define our Queries to add users to database.
        add_user_query = "INSERT INTO users VALUES (:uid, :name, :pwd)"
        new_artist_query = "INSERT INTO artists VALUES (:uid, :name, :nat, :pwd)"

        print("users:\n", all_current_users, "\nartists:", all_current_artists)

        while True:
            username = input("Please Enter A Username: ")

            if [usr for usr in all_current_users if username in usr] \
                    or [usr for usr in all_current_artists if username in usr]:
                print("\nSorry, that username has already been taken. Please try another one:")
            else:
                name = input("Username is available!\nWhat should we call you? (Name)\n")
                confirm = input( "Username: " + username + "\nName: " + name + "\nCorrect? (y/n/q)")
                if confirm.lower() == 'y':
                    break
                elif confirm.lower() == 'q':
                    return
        password = hash_password(input("Please enter a password:\n "))
        self.cursor.execute(add_user_query, {'uid': username, 'name': name, 'pwd': password})
        self.connection.commit()
        # todo Add error catching here
        print("User has been created successfully!")

    def get_authentication(self):
        while True:
            user_name = input("\n\nPlease Enter Your Username: \n")
            user_password = input("Please Enter Your Password:\n")
            user_password = hash_password(user_password)
            self.cursor.execute('''
            SELECT * FROM users WHERE uid = :uname AND pwd = :pw;''', {'uname': user_name, 'pw': user_password}, )
            users = self.cursor.fetchall()
            self.cursor.execute('''
            SELECT * FROM artists WHERE aid = :uname AND pwd = :pw;''', {'uname': user_name, 'pw': user_password}, )
            artists = self.cursor.fetchall()
            if len(users) != 1 and len(artists) != 1:
                print("User could not be authenticated.")
                return [], []
            else:
                return users, artists

    def load_all_names(self):
        self.cursor.execute('''
        SELECT uid FROM users;''')
        users = self.cursor.fetchall()
        self.cursor.execute('''
        SELECT aid FROM artists;''')
        artists = self.cursor.fetchall()
        return users, artists
