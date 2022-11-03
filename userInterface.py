from os import system, name
from datetime import datetime, timezone
import sqlite3
import time
import random


def clear_screen():
    if name == 'nt':
        _ = system('cls')

        # for mac and linux(here, os.name is 'posix')
    else:
        _ = system('clear')


def order_output(results, user_input=None):
    output = []
    
    
    for i in range(len(results)):
        output.append([0, results[i]])

    if user_input is not None:
        for i in range(len(results)):
            for j in range(len(user_input)):
                if user_input[j].lower() in results[i][1].lower():
                    output[i][0] += 1
                
    output.sort(reverse=True)
    return output


    

def select_key_id(results):
    sid = []
    for i in range(len(results)):
        sid.append(results[i][1][0])
    return sid

def select_snos(results):
    sid = []
    for i in range(len(results)):
        sid.append(results[i][0])
    return sid


class UserInterface:

    def __init__(self, cursor, connection, user_info):
        self.cursor = cursor
        self.connection = connection
        self.user_info = user_info
        self.sessionStart = None
        self.sessionEnd = 'NULL'
        self.sessionNumber = None


    def launch_home_screen(self, message=None):
        clear_screen()

        if message is not None:
            print(message)
        # <todo> add option to search for songs/playlists or artists and end session.
        user_choice = input("Welcome " + self.user_info[1] +
                            '''\nMake a selection:
                            (1): Search for songs/playlists
                            (2): Search for artists
                            (3): Start Session
                            (4): End session\n''')
        if user_choice == '1':
            self.search_songs()
        elif user_choice == '2':
            self.search_artist()
        elif user_choice == '3':
            self.start_new_session()
            self.launch_home_screen()
        elif user_choice == '4':
            if self.sessionStart is not None:
                self.sessionEnd = datetime.now(timezone.utc)
                self.log_user_out()
        else:
            self.launch_home_screen()

    def start_new_session(self):
        try:
            self.sessionStart = datetime.now(timezone.utc)
            self.cursor.execute('''
                SELECT sno FROM sessions WHERE uid = '{0}';'''.format(self.user_info[0]))
            already_generated_snos = select_snos(self.cursor.fetchall())

            self.sessionNumber = random.randint(0, 9223372036854775807)

            while self.sessionNumber in already_generated_snos:
                self.sessionNumber = random.randint(0, 9223372036854775807)

            self.cursor.execute('''
                                        INSERT INTO sessions (uid, sno, start, end)
                                        VALUES ('{0}',{1},'{2}','{3}')
                                        '''.format(self.user_info[0], self.sessionNumber, self.sessionStart, self.sessionEnd))
            self.connection.commit()
        except sqlite3.Error as e:
            print(e)

    def log_user_out(self):
        try:
            self.cursor.execute('''
                        UPDATE sessions
                        SET end = '{2}'
                        WHERE uid = '{0}' AND sno = {1}
                        '''.format(self.user_info[0], self.sessionNumber, self.sessionEnd))
            self.connection.commit()
        except sqlite3.Error as e:
            print(e)

    def search_songs(self):
        try:
            user_input = input("Please enter song.....\n").split()
            query = '''
                        select * from songs where title like '%{0}%'
                        '''.format(user_input[0])
            for i in range(1, len(user_input)):
                query = query + '''
                        union
                        select * from songs where title like '%{0}%'
                        '''.format(user_input[i])
            query = query + '''
                        union
                        select * from playlists where title like '%{0}%'
                        '''.format(user_input[0])
            for i in range(1, len(user_input)):
                query = query + '''
                        union
                        select * from playlists where title like '%{0}%'
                        '''.format(user_input[i])

            self.cursor.execute(query)
            results = order_output(self.cursor.fetchall(), user_input)
            user_selection = self.song_choices(results, select_key_id(results))
            if user_selection is not None:
                self.song_action(user_selection)
            else:
                self.launch_home_screen("No results found or quite command heard")
        except sqlite3.Error as e:
            print(e)

    def song_choices(self, results, possible_ids):
        if len(results) == 0:
            return None
        playlist_ids = []
        start_index = 0
        end_index = start_index + 4 if (start_index + 4) < len(results) else len(results) - 1
        max_index = len(results) - 1
        while True:
            for i in range(start_index, end_index + 1):
                if isinstance(results[i][1][2], int):
                    print(results[i][1][0], results[i][1][1], results[i][1][2], "<- Song")
                else:
                    print(results[i][1][0], results[i][1][1], results[i][1][2], "<- Playlist")
                    playlist_ids.append(results[i][1][0])
            print("Showing " + str(start_index + 1) + "-" + str(end_index + 1) + "/" + str(len(results)) + " results")
            user_choice = input("Enter ID of song/playlist, or 'n' for next page, 'p' for previous page\n")
            clear_screen()
            if user_choice == 'n':
                if max_index - end_index > 0:
                    end_index = end_index + 5 if end_index + 5 < max_index else end_index + (
                                len(results) - end_index) - 1
                    start_index = len(results) - 5

            elif user_choice == 'p':
                start_index = start_index - 5 if start_index - 5 > 0 else 0
                end_index = start_index + 4 if (start_index + 4) < len(results) else max_index
            elif user_choice.isdigit():
                if int(user_choice) in possible_ids:
                    if int(user_choice) in playlist_ids:
                        try:
                            self.cursor.execute('''
                                            SELECT sid, title, duration
                                            FROM songs
                                            WHERE sid IN (SELECT sid FROM plinclude WHERE pid = {0})
                                            '''.format(user_choice))
                            results = self.cursor.fetchall()
                            results = order_output( results )
                            possible_ids = select_key_id(results)
                            user_choice = self.song_choices(results,possible_ids )
                        except sqlite3.Error as e:
                            print(e)
                    return user_choice
            elif user_choice.lower() == 'q':
                return None
            else:
                print("Sorry, the choice you entered could not be recognized, please try again.")

    def song_action(self, user_selection):
        '''
        -- search_data is a list of possible sid's from the search_songs_Playlists() function
        -- Uses data from search_songs_Playlists()
        -- User can perform any of these 3 actions after picking which song from the search results
        -- 1) listen to it
            -- if selected for listening, a listening event is recorded within the current session.
            -- a listening event is recorded by either inserting a row to table listen or increasing the listen count of the song by 1

        -- 2) See more information about the song
            -- artist(s) who performed the song, song id, title, duration, names of playlists song is in
        -- 3) Add the song to a playlist
            -- when adding a song to a new playlist, a new playlist should be created with a unique id (created by the system) and the uid set to the user who created it
        '''
        try:
            song_choice = int(user_selection)
            uid = self.user_info[0]

            print("1) Listen to it")
            print("2) See more information about the song")
            print("3) Add the song to a playlist")
            print("4) back to search Results")
            action = int(input("What would you like to do? (enter the number of your choice): "))
            if action == 1:
                if self.sessionStart is None:
                    self.start_new_session()

                self.cursor.execute('''
                                        SELECT * FROM listen
                                        WHERE uid = '{0}' AND sid = '{1}' AND sno = {2}
                                        '''.format(uid, song_choice, self.sessionNumber))
                listen = self.cursor.fetchall()
                if len(listen) == 0:
                    self.cursor.execute('''
                                            INSERT INTO listen (uid, sno, sid, cnt)
                                            VALUES ('{0}', {2}, '{1}', 1)
                                            '''.format(uid, song_choice, self.sessionNumber))
                else:
                    self.cursor.execute('''
                                            UPDATE listen
                                            SET cnt = cnt + 1
                                            WHERE uid = '{0}' AND sid = '{1}' AND sno={2}
                                            '''.format(uid, song_choice, self.sessionNumber))

                self.connection.commit()

                self.launch_home_screen("Song added to listening history")
            elif action == 2:
                self.cursor.execute('''
                SELECT * FROM songs WHERE sid = {0}
                '''.format(song_choice))

                results = self.cursor.fetchall()
                print("Song Name:")
                for row in results:
                    print(row[1])
                self.cursor.execute('''
                SELECT * FROM artists WHERE aid IN (SELECT aid FROM perform WHERE sid = {0})
                '''.format(song_choice))
                results = self.cursor.fetchall()
                print("Artists: ")
                for row in results:
                    print(row[1])
                self.cursor.execute('''
                SELECT * FROM playlists WHERE pid IN (SELECT pid FROM plinclude WHERE sid = {0})
                '''.format(song_choice))
                results = self.cursor.fetchall()
                print("Playlists: ")
                for row in results:
                    print(row[1])
                input("Press Enter to go back to main screen")
                self.launch_home_screen()
            elif action == 3:
                print("User Id", uid)
                self.cursor.execute('''
                SELECT * FROM playlists WHERE uid = '{0}'
                '''.format(uid))
                results = self.cursor.fetchall()
                print("Existing Playlists: ")
                for row in results:
                    print(row[0], row[1])

                new_playlist = input("Would you like to create a new playlist? (y/n): ")
                if new_playlist == "y":
                    # set pid to the size of the playlists table + 1
                    self.cursor.execute('''
                    SELECT * FROM playlists
                    ''')
                    results = self.cursor.fetchall()
                    pid = len(results) + 1
                    new_playlist_name = input("Enter a name for your new playlist: ")
                    self.cursor.execute('''
                    INSERT INTO playlists (pid, title, uid)
                    VALUES ({0}, "{1}", "{2}")
                    '''.format(pid, new_playlist_name, uid))
                    self.connection.commit()
                    print("Song added to new playlist")
                if new_playlist == "n":
                    pid = input("Enter the pid of the playlist you want to add the song to: ")
                    # check the largest sorder in the playlist and add 1 to it

                    self.cursor.execute(
                        '''SELECT * FROM plinclude WHERE pid = {0}'''.format(pid))
                    results = self.cursor.fetchall()
                    sorder = len(results) + 1
                    self.cursor.execute('''
                    INSERT OR IGNORE INTO plinclude (pid, sid, sorder)
                    VALUES ({0}, {1}, {2})
                    '''.format(pid, song_choice, sorder))
                    self.connection.commit()
                    print("Song added to playlist")
                self.launch_home_screen()

            elif action == 4:
                self.launch_home_screen()
        except sqlite3.Error as e:
            print(e)


    def search_artist(self):
        try:
            user_input = input("search for artists: ")

            # user_input = "love cold fire"

            user_input = user_input.split()
            query = '''
                select * from artists where name like '%{0}%'
                '''.format(user_input[0])
            for i in range(1, len(user_input)):
                query = query + '''
                union
                select * from artists where name like '%{0}%'
                '''.format(user_input[i])
            query = query + '''
                union
                select * from artists where aid IN (SELECT aid FROM perform WHERE perform.sid IN (SELECT sid FROM songs WHERE title like '%{0}%'))
                '''.format(user_input[0])
            for i in range(1, len(user_input)):
                query = query + '''
                union
                select * from artists where aid IN (SELECT aid FROM perform WHERE perform.sid IN (SELECT sid FROM songs WHERE title like '%{0}%'))
                '''.format(user_input[i])

            self.cursor.execute(query)
            results = self.cursor.fetchall()
            results = order_output(results, user_input)
            selectable_AID = select_key_id(results)

            print("Results:")
            if len(results) == 0:
                clear_screen()
                print("No Artist Found")
                self.launch_home_screen()
            else:
                selection_choice = self.artist_choices(results, selectable_AID)
                if selection_choice is None:
                    self.launch_home_screen()
                else:
                    self.cursor.execute('''
                        SELECT sid, title, duration FROM songs WHERE sid IN (SELECT sid FROM perform WHERE aid = "{0}")
                        '''.format(selection_choice))
                    results = self.cursor.fetchall()
                    results = order_output( results )

                    user_selection = self.song_choices(results, select_key_id(results))

                    if user_selection is not None:
                        self.song_action(user_selection)
                    else:
                        self.launch_home_screen
        except sqlite3.Error as e:
            print(e)



    def artist_choices(self, results, possible_ids):
        start_index = 0
        end_index = start_index + 4 if (start_index + 4) < len(results) else len(results) - 1
        max_index = len(results) - 1
        while True:
            for i in range(start_index, end_index + 1):
                print(results[i][1][0], results[i][1][1], results[i][1][2])
            print("Showing " + str(start_index + 1) + "-" + str(end_index + 1) + "/" + str(len(results)) + " results")
            user_choice = input("Enter ID of song/playlist, or 'n' for next page, 'p' for previous page\n")
            clear_screen()
            if user_choice == 'n':
                if max_index - end_index > 0:
                    end_index = end_index + 5 if end_index + 5 < max_index else end_index + (
                                len(results) - end_index) - 1
                    start_index = len(results) - 5

            elif user_choice == 'p':
                start_index = start_index - 5 if start_index - 5 > 0 else 0
                end_index = start_index + 4 if (start_index + 4) < len(results) else max_index
            elif user_choice in possible_ids:
                return user_choice
            elif user_choice.lower() == 'q':
                return None
            else:
                print("Sorry, the choice you entered could not be recognized, please try again.")