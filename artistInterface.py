from os import system, name
from datetime import datetime, timezone
import time
import random

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
        clear_screen()
        if message is not None:
            print(message)
        user_choice = input("Welcome Artist! What would you like to do today?\n" + ''' \nMake a selection:
        (1): Add a new song
        (2): View artist statistics
        (3): Edit session \n
                            ''')
        if user_choice == '1':
            self.add_song()

        elif user_choice == '2':
            self.search_artist()
        
        elif user_choice == '3':
            self.log_artist_out()

    def top_3_stats(self):
         
          
          aid = self.user_input[0]
          self.cursor.execute('''
          SELECT uid, SUM(cnt) FROM listen WHERE sid IN (SELECT sid FROM perform WHERE aid = "{0}") GROUP BY uid ORDER BY SUM(cnt) DESC LIMIT 3
          '''.format(aid))
          results = cursor.fetchall()
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
    def add_song(self):
        global connection, cursor
        #test uid
        aid = self.artist_info[0]
        
        #set sid to the size of the songs table + 1
        cursor.execute('''
        SELECT * FROM songs
        ''')
        results = cursor.fetchall()
        sid = len(results) + 1
        #set nationality to the artist's nationality who is logged in
        cursor.execute('''
        SELECT nationality FROM artists WHERE aid like '{0}'
        '''.format(aid))
        results = cursor.fetchall()
        nationality = results[0][0]
        #set title to the title entered by the artist
        title = input("Enter the title of the song: ")
        #set duration to the duration entered by the artist
        duration = int(input("Enter the duration of the song: "))
        #set aid to the aid of the artist who is logged in
        cursor.execute('''
        SELECT aid FROM artists WHERE aid like '{0}'
        '''.format(aid))
        results = cursor.fetchall()
        aid = results[0][0]
        # check if a song with the same title and performed by the same artist exists
        cursor.execute('''
        SELECT * FROM songs WHERE title like '{0}' AND sid IN (SELECT sid FROM perform WHERE aid like '{1}')
        '''.format(title.lower(), aid))
        results = cursor.fetchall()
        
        if len(results) > 0:
            artist_choice = input("would you still like to add this song despite the conflict? (1/2): ")
            if artist_choice == "1":
                #insert the song into the songs table
                cursor.execute('''
                INSERT INTO songs (sid, title, duration, type)
                VALUES ({0}, "{1}", {2}, "song")
                '''.format(sid, title, duration))
                #insert the artist into the perform table
                cursor.execute('''
                INSERT INTO perform (aid, sid)
                VALUES ("{0}", {1})
                '''.format(aid, sid))
                connection.commit()
                #ask if the artist wants to add any other artists to the song
                add_more_artists = input("Would you like to add any other artists to this song? (y/n): ")
                if add_more_artists == "y":
                    add_more_artists = True
                else:
                    add_more_artists = False
                while add_more_artists == True:
                    #ask for the aid of the artist to be added
                    aid = input("Enter the aid of the artist you would like to add: ")
                    #insert the artist into the perform table
                    cursor.execute('''
                    INSERT INTO perform (aid, sid)
                    VALUES ({0}, {1})
                    '''.format(aid, sid))
                    connection.commit()
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
                cursor.execute('''
                INSERT INTO songs (sid, title, duration, type)
                VALUES ({0}, "{1}", {2}, "song")
                '''.format(sid, title, duration))
                #insert the artist into the perform table
                cursor.execute('''
                INSERT INTO perform (aid, sid)
                VALUES ("{0}", {1})
                '''.format(aid, sid))
                connection.commit()
                #ask if the artist wants to add any other artists to the song
                add_more_artists = input("Would you like to add any other artists to this song? (y/n): ")
                if add_more_artists == "y":
                    add_more_artists = True
                else:
                    add_more_artists = False
                while add_more_artists == True:
                    #ask for the aid of the artist to be added
                    aid = input("Enter the aid of the artist you would like to add: ")
                    #insert the artist into the perform table
                    cursor.execute('''
                    INSERT INTO perform (aid, sid)
                    VALUES ({0}, {1})
                    '''.format(aid, sid))
                    connection.commit()
                    #ask if the artist wants to add any other artists to the song
                    add_more_artists = input("Would you like to add any other artists to this song? (y/n):")
                    if add_more_artists == "y":
                        add_more_artists = True
                    else:
                        add_more_artists = False
        
        


def artist_action():
    global connection, cursor
    '''
    -- Artist actions:
    -- 1) Add Song
            -- artist/user provides a title and duration
            -- new song gets assigned a unique SID by the system
            -- allow other artists to be included in the song
            -- allow the song to be added to a playlist
    -- 2) Check top 3 users/playlists for an artist
            -- show top 3 listeners based on longest listening time
            -- show top 3 playlists based on number of songs in the playlist
            
    '''
    
    def add_song():
        global connection, cursor
        #test uid
        aid = 'a9'
        
        #set sid to the size of the songs table + 1
        cursor.execute('''
        SELECT * FROM songs
        ''')
        results = cursor.fetchall()
        sid = len(results) + 1
        #set nationality to the artist's nationality who is logged in
        cursor.execute('''
        SELECT nationality FROM artists WHERE aid like '{0}'
        '''.format(aid))
        results = cursor.fetchall()
        nationality = results[0][0]
        #set title to the title entered by the artist
        title = input("Enter the title of the song: ")
        #set duration to the duration entered by the artist
        duration = int(input("Enter the duration of the song: "))
        #set aid to the aid of the artist who is logged in
        cursor.execute('''
        SELECT aid FROM artists WHERE aid like '{0}'
        '''.format(aid))
        results = cursor.fetchall()
        aid = results[0][0]
        # check if a song with the same title and performed by the same artist exists
        cursor.execute('''
        SELECT * FROM songs WHERE title like '{0}' AND sid IN (SELECT sid FROM perform WHERE aid like '{1}')
        '''.format(title.lower(), aid))
        results = cursor.fetchall()
        
        if len(results) > 0:
            artist_choice = input("would you still like to add this song despite the conflict? (1/2): ")
            if artist_choice == "1":
                #insert the song into the songs table
                cursor.execute('''
                INSERT INTO songs (sid, title, duration, type)
                VALUES ({0}, "{1}", {2}, "song")
                '''.format(sid, title, duration))
                #insert the artist into the perform table
                cursor.execute('''
                INSERT INTO perform (aid, sid)
                VALUES ("{0}", {1})
                '''.format(aid, sid))
                connection.commit()
                #ask if the artist wants to add any other artists to the song
                add_more_artists = input("Would you like to add any other artists to this song? (y/n): ")
                if add_more_artists == "y":
                    add_more_artists = True
                else:
                    add_more_artists = False
                while add_more_artists == True:
                    #ask for the aid of the artist to be added
                    aid = input("Enter the aid of the artist you would like to add: ")
                    #insert the artist into the perform table
                    cursor.execute('''
                    INSERT INTO perform (aid, sid)
                    VALUES ({0}, {1})
                    '''.format(aid, sid))
                    connection.commit()
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
                cursor.execute('''
                INSERT INTO songs (sid, title, duration, type)
                VALUES ({0}, "{1}", {2}, "song")
                '''.format(sid, title, duration))
                #insert the artist into the perform table
                cursor.execute('''
                INSERT INTO perform (aid, sid)
                VALUES ("{0}", {1})
                '''.format(aid, sid))
                connection.commit()
                #ask if the artist wants to add any other artists to the song
                add_more_artists = input("Would you like to add any other artists to this song? (y/n): ")
                if add_more_artists == "y":
                    add_more_artists = True
                else:
                    add_more_artists = False
                while add_more_artists == True:
                    #ask for the aid of the artist to be added
                    aid = input("Enter the aid of the artist you would like to add: ")
                    #insert the artist into the perform table
                    cursor.execute('''
                    INSERT INTO perform (aid, sid)
                    VALUES ({0}, {1})
                    '''.format(aid, sid))
                    connection.commit()
                    #ask if the artist wants to add any other artists to the song
                    add_more_artists = input("Would you like to add any other artists to this song? (y/n):")
                    if add_more_artists == "y":
                        add_more_artists = True
                    else:
                        add_more_artists = False
        
        connection.commit()