from os import system, name
from datetime import datetime, timezone
import time
import random
import sqlite3

def clear_screen():
    if name == 'nt':
        _ = system('cls')

        # for mac and linux(here, os.name is 'posix')
    else:
        _ = system('clear')

class ArtistInterface:
    def __init__(self, cursor, connection, artist_info):
        self.cursor = cursor
        self.connection = connection
        self.artist_info = artist_info
    def launch_home_screen(self, message = None):
        if message is not None:
            print(message)
        user_choice = input("Welcome "+ self.artist_info[1] + "! What would you like to do today?\n" + ''' \nMake a selection:
        (1): Add a new song
        (2): View artist statistics
        (3): Exit \n
                            ''')
        if user_choice == '1':
            self.add_song()

        elif user_choice == '2':
            self.top_3_stats()
        
        elif user_choice == '3':
            clear_screen()
            return

    def top_3_stats(self):
         
          try:
              aid = self.artist_info[0]
              self.cursor.execute('''
              SELECT uid, SUM(cnt) FROM listen WHERE sid IN (SELECT sid FROM perform WHERE aid = "{0}") GROUP BY uid ORDER BY SUM(cnt) DESC LIMIT 3
              '''.format(aid))
              results = self.cursor.fetchall()
              print("Top 3 users based on longest listening time: ")
              for row in results:
                  print(row[0], row[1])
              self.cursor.execute('''
              SELECT pid, COUNT(sid) FROM plinclude WHERE sid IN (SELECT sid FROM perform WHERE aid = "{0}") GROUP BY pid ORDER BY COUNT(sid) DESC LIMIT 3
              '''.format(aid))
              results = self.cursor.fetchall()
              print("Top 3 playlists based on number of songs in the playlist: ")
              for row in results:
                  print(row[0], row[1])
              self.launch_home_screen()
          except sqlite3.Error as e:
              print(e)

    def add_song(self):
        try:
            #test uid
            aid = self.artist_info[0]

            #set sid to the size of the songs table + 1
            self.cursor.execute('''
            SELECT * FROM songs
            ''')
            results = self.cursor.fetchall()
            sid = len(results) + 1
            #set nationality to the artist's nationality who is logged in
            self.cursor.execute('''
            SELECT nationality FROM artists WHERE aid like '{0}'
            '''.format(aid))
            results = self.cursor.fetchall()
            nationality = results[0][0]
            #set title to the title entered by the artist
            title = input("Enter the title of the song: ")
            #set duration to the duration entered by the artist
            duration = int(input("Enter the duration of the song: "))
            #set aid to the aid of the artist who is logged in
            self.cursor.execute('''
            SELECT aid FROM artists WHERE aid like '{0}'
            '''.format(aid))
            results = self.cursor.fetchall()
            aid = results[0][0]
            # check if a song with the same title and performed by the same artist exists
            self.cursor.execute('''
            SELECT * FROM songs WHERE title like '{0}' AND sid IN (SELECT sid FROM perform WHERE aid like '{1}')
            '''.format(title.lower(), aid))
            results = self.cursor.fetchall()

            if len(results) > 0:
                artist_choice = input("would you still like to add this song despite the conflict? (y/n): ")
                if artist_choice == "y":
                    #insert the song into the songs table
                    self.cursor.execute('''
                    INSERT INTO songs (sid, title, duration)
                    VALUES ({0}, "{1}", {2})
                    '''.format(sid, title, duration))
                    #insert the artist into the perform table
                    self.cursor.execute('''
                    INSERT INTO perform (aid, sid)
                    VALUES ("{0}", {1})
                    '''.format(aid, sid))
                    self.connection.commit()
                    #ask if the artist wants to add any other artists to the song
                    add_more_artists = input("Would you like to add any other artists to this song? (y/n): ")
                    if add_more_artists == "y":
                        add_more_artists = True
                    else:
                        add_more_artists = False
                    while add_more_artists == True:
                        #ask for the aid of the artist to be added
                        aid = input("Enter the aid of the artist you would like to add: ")
                        self.cursor.execute('''
                                    SELECT aid
                                    FROM artists
                                    WHERE aid = '{0}'
                                    '''.format(aid))
                        results = self.cursor.fetchall()
                        if len(results) > 0:
                            #insert the artist into the perform table
                            self.cursor.execute('''
                            INSERT INTO perform (aid, sid)
                            VALUES ({0}, {1})
                            '''.format(aid, sid))
                            self.connection.commit()
                        else:
                            clear_screen()
                            print(" Artist ID Not Recognized!")
                        #ask if the artist wants to add any other artists to the song
                        add_more_artists = input("Would you like to add any other artists to this song? (y/n):")
                        if add_more_artists == "y":
                            add_more_artists = True
                        else:
                            add_more_artists = False
                else:
                    print("Song not added")
            else:
                #insert the song into the songs table
                    self.cursor.execute('''
                    INSERT INTO songs (sid, title, duration)
                    VALUES ({0}, "{1}", {2})
                    '''.format(sid, title, duration))
                    #insert the artist into the perform table
                    self.cursor.execute('''
                    INSERT INTO perform (aid, sid)
                    VALUES ("{0}", {1})
                    '''.format(aid, sid))
                    self.connection.commit()
                    #ask if the artist wants to add any other artists to the song
                    add_more_artists = input("Would you like to add any other artists to this song? (y/n): ")
                    if add_more_artists == "y":
                        add_more_artists = True
                    else:
                        add_more_artists = False
                    while add_more_artists == True:
                        #ask for the aid of the artist to be added
                        aid = input("Enter the aid of the artist you would like to add: ")
                        self.cursor.execute('''
                                                        SELECT aid
                                                        FROM artists
                                                        WHERE aid = '{0}'
                                                        '''.format(aid))
                        results = self.cursor.fetchall()
                        if len(results) > 0:
                            # insert the artist into the perform table
                            self.cursor.execute('''
                                                INSERT INTO perform (aid, sid)
                                                VALUES ('{0}', {1})
                                                '''.format(aid, sid))
                            self.connection.commit()
                        else:
                            clear_screen()
                            print(" Artist ID Not Recognized!")
                        #ask if the artist wants to add any other artists to the song
                        add_more_artists = input("Would you like to add any other artists to this song? (y/n):")
                        if add_more_artists == "y":
                            add_more_artists = True
                        else:
                            add_more_artists = False
            self.launch_home_screen()
        except sqlite3.Error as e:
            print(e)