import sqlite3
import hashlib


def hash_password(password):
    alg = hashlib.sha256()
    alg.update(password.encode('utf-8'))
    return alg.hexdigest()


def get_authentication(cursor, connection):
    debug_code = input('Debug?\n0: Yes\n1: No\n')

    if debug_code == '0':
        username = input("Enter username:\n")
        password = input("Enter password: \n")
        password = hash_password( password )
        access = input("Enter access: \n")
        cursor.execute('''
        INSERT INTO users (uid, authcode, access) values
        (:username, :password_hashed, :access);''',{'username':username,'password_hashed':password,'access':access})

    elif debug_code == '1':
        user_name = input("\n\nPlease Enter Your Username: \n")
        user_password = input("Please Enter Your Password:\n")
        user_password = hash_password( user_password )
        cursor.execute('''
        SELECT * FROM users WHERE uid = :uname AND authcode = :pw;''', {'uname': user_name, 'pw': user_password}, )
        ans = cursor.fetchall()
        if len(ans) != 1:
            print("Authentication Failed")
            return False
        elif ans[0][2]==0:
            print("You have no access")
        elif ans[0][2] == 1:
            print("You are a user")
        elif ans[0][2] == 2:
            print("You are an artist")
        elif ans[0][2] == 3:
            print("You are both")
        else:
            print("EEEEERRR")

    return True


def check_access():
    # Get the users interface access after they have been authenticated.
    pass
