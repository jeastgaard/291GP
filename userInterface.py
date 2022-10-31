def order_output(results, user_input):
    output = []
    for i in range(len(results)):
        output.append([0, results[i]])
    for i in range(len(results)):
        for j in range(len(user_input)):
            if user_input[j].lower() in results[i][1].lower():
                output[i][0] += 1
    output.sort(reverse = True)
    return output

def select_AID(results):
    aid = []
    for i in range(len(results)):
            aid.append(results[i][1][0])
    return aid

def select_SID(results):
    sid = []
    for i in range(len(results)):
            sid.append(results[i][1][0])
    return sid
class UserInterface:

    def __init__(self, cursor, connection, user_info):
        self.cursor = cursor
        self.connection = connection
        self.user_info = user_info

    def launch_home_screen(self):
        # <todo> add option to search for songs/playlists or artists and end session.
        user_choice = input("Welcome " + self.user_info[0][1] +
                            '''Make a selection:
                            (1): Search for songs/playlists
                            (2): Search for artists
                            (3): End session''')
        if user_choice == '1':
            self.search_songs()
        elif user_choice == '2':
            self.search_artist()

    def search_songs(self):

        user_input = input("Please enter song.....").split()
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
        for i in range(len(results)):
            if isinstance(results[i][1][2], int):
                print(results[i][1][0], results[i][1][1], results[i][1][2], "<- Song")
            else:
                print(results[i][1][0], results[i][1][1], results[i][1][2], "<- Playlist")

        self.song_action( select_SID(results ))

    def song_action(self, search_data):
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

        song_choice = input("Which of the above songs do you want to select? (enter song id): ")
        song_choice = int(song_choice)
        uid = self.user_info[0]
        if song_choice in search_data:

            print("1) Listen to it")
            print("2) See more information about the song")
            print("3) Add the song to a playlist")
            action = int(input("What would you like to do? (enter the number of your choice): "))
            if action == 1:
                self.cursor.execute('''
                INSERT INTO listen (uid, sno, sid, cnt)
                VALUES ('{0}', (SELECT COUNT(*) FROM listen WHERE uid = '{0}' AND sid = {1}) + 1, {1}, 1)
                '''.format(uid, song_choice))
                self.connection.commit()
                print("Song added to listening history")
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
            elif action == 3:
                print( "User Id", uid)
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

    def search_artist(self):
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
        results = order_output( results, user_input )
        selectable_AID = select_AID(results)

        print("Results:")
        for i in range(len(results)):
            if i < 5:
                # <todo> Total songs performed ( add new query )
                # <todo> Print like: | aid | name | Nationality | total songs per.|
                # <todo> Print like: | .... | ... | ... | ...|
                # <todo> Print like: | .... | ... | ... | ...|
                # <todo> Print like: | .... | ... | ... | ...|
                # <todo> Print like: | .... | ... | ... | ...|
                # <todo> Print like: | .... | ... | ... | ...|
                # <todo> Showing 5 of #, press........
                print(results[i][1][0], results[i][1][1], results[i][1][2])

        # if len(selectable_AID) > 0:
        #     select_artist(selectable_AID)