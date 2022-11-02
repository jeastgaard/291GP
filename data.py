import sqlite3

#Tables
#users(uid, name, pwd)
#songs(sid, title, duration)
#sessions(uid, sno, start, end)
#listen(uid, sno, sid, cnt)
#playlists(pid, title, uid)
#plinclude(pid, sid, sorder)
#artists(aid, name, nationality, pwd)
#perform(aid, sid)

connection = None
cursor = None

def main():
    global connection, cursor
    path = './project1.db'
    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    
    #define_tables()
    #insert_data()
    
    
    
    #test 1:search for a song / playlist and then perform an action on it
    #search_songs_Playlists()
    
    #test 2: search for an artist
    # search_artist()
    
    #test 3: artist actions
    artist_action()
    
    
    connection.commit()
    return

def select_SID(results):
    sid = []
    for i in range(len(results)):
        if results[i][1][3] == "song":
            sid.append(results[i][1][0])
    return sid
#function for searching songs and playlists
def search_songs_Playlists():
    global connection, cursor
    
    '''
    -- User provides 1 or more unique keywords 
    -- System retrieves all songs and playlists that have any of the given keywords
    -- for each song, return the song id, title, and duration
    -- for each playlist, return the playlist id, title, and total duration of all songs in the playlist
    -- each row should indicate whether the result is a song or a playlist
    -- result should be ordered based on the number of matching keywords with the song/playlist with the most matches displayed first
    -- if there are more than 5 matching songs/playlists, show the first 5 or let the user choose to see more matches. 
    -- if a user selects a song, perform a song_action()
    -- if a user selects a playlist, display the id, title, and duration of all songs in he playlist and the user should be able to perform a song_action()
    
    '''
    
    def tableUpdate():
        global connection, cursor
        cursor.execute( 'ALTER TABLE {tn} ADD COLUMN {cn} {ct}'\
                .format( tn="songs", cn="type", ct="String" ) )
        connection.commit()
        cursor.execute( 'ALTER TABLE {tn} ADD COLUMN {cn} {ct}'\
                .format( tn="playlists", cn="type", ct="String"))
        connection.commit()
        cursor.execute('''
                    UPDATE songs
                    SET type = "song"
                    
                    ''')
        connection.commit()
        cursor.execute('''
                    UPDATE playlists
                    SET type = "playlist"
                                                                    
                    ''')
        
        
        
        connection.commit()
    
    def add_Song_total_playlists():
        global connection, cursor
        cursor.execute( 'ALTER TABLE {tn} ADD COLUMN {cn} {ct}'\
                .format( tn="songs", cn="total_playlists", ct="int" ) )
        connection.commit()
        cursor.execute('''
                    UPDATE songs
                    SET total_playlists = (SELECT COUNT(*) FROM plinclude WHERE plinclude.sid = songs.sid)
                    ''')
        connection.commit()
    
    def add_Playlist_total_song_duration():
        global connection, cursor
        cursor.execute('''
                    ALTER TABLE playlists
                    ADD COLUMN total_duration INT
                    ''')
        connection.commit()
        cursor.execute('''
                    UPDATE playlists
                    SET total_duration = (SELECT SUM(duration) FROM songs WHERE sid IN (SELECT sid FROM plinclude WHERE pid = playlists.pid))
                    ''')
        connection.commit()
    
    
    tableUpdate()
    add_Song_total_playlists()
    add_Playlist_total_song_duration()
    
    
    user_input = input("search for songs or playlists: ")
  

    user_input = user_input.split()
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
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    def orderOutput(results):
        output = []
        for i in range(len(results)):
            output.append([0, results[i]])
        for i in range(len(results)):
            for j in range(len(user_input)):
                if user_input[j].lower() in results[i][1].lower():
                    output[i][0] += 1
        output.sort(reverse = True)
        return output
    

    
    print("Search Results:")
    results = orderOutput(results)
    selectable_songs = select_SID(results)
    for i in range(len(results)):
        if i < 5:
            if results[i][1][3] == "song":
                print( results[i][1][3], results[i][1][0], results[i][1][1], results[i][1][2])
            else:
                print( results[i][1][3], results[i][1][0], results[i][1][1], results[i][1][4])
    #song_action()
 
    connection.commit()
    
#function for song action
def song_action(search_data):
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
    global connection, cursor

    #test uid
    uid = 'u9'


    song_choice = input("Which of the above songs do you want to select? (enter song id): ")
    song_choice = int(song_choice)
    
    if song_choice in search_data:
       
        print("1) Listen to it")
        print("2) See more information about the song")
        print("3) Add the song to a playlist")
        action = int(input("What would you like to do? (enter the number of your choice): "))
        if action == 1:
            cursor.execute('''
            INSERT INTO listen (uid, sno, sid, cnt)
            VALUES ('{0}', (SELECT COUNT(*) FROM listen WHERE uid = '{0}' AND sid = {1}) + 1, {1}, 1)
            '''.format(uid, song_choice))
            connection.commit()
            print("Song added to listening history")
        elif action == 2:
            cursor.execute('''
            SELECT * FROM songs WHERE sid = {0}
            '''.format(song_choice))
            
            results = cursor.fetchall()
            print("Song Name:")
            for row in results:
                print(row[1])
            cursor.execute('''
            SELECT * FROM artists WHERE aid IN (SELECT aid FROM perform WHERE sid = {0})
            '''.format(song_choice))
            results = cursor.fetchall()
            print("Artists: ")
            for row in results:
                print(row[1])
            cursor.execute('''
            SELECT * FROM playlists WHERE pid IN (SELECT pid FROM plinclude WHERE sid = {0})
            '''.format(song_choice))
            results = cursor.fetchall()
            print("Playlists: ")
            for row in results:
                print(row[1])
        elif action == 3:
            cursor.execute('''
            SELECT * FROM playlists WHERE uid like '{0}'
            '''.format(uid))
            results = cursor.fetchall()
            print("Existing Playlists: ")
            for row in results:
                print(row[0],row[1])
            
            new_playlist = input("Would you like to create a new playlist? (y/n): ")
            if new_playlist == "y":
                #set pid to the size of the playlists table + 1
                cursor.execute('''
                SELECT * FROM playlists
                ''')
                results = cursor.fetchall()
                pid = len(results) + 1
                new_playlist_name = input("Enter a name for your new playlist: ")
                cursor.execute('''
                INSERT INTO playlists (pid, title, uid)
                VALUES ({0}, "{1}", "{2}")
                '''.format(pid, new_playlist_name, uid))
                connection.commit()
                print("Song added to new playlist")
            if new_playlist == "n":
                pid = input("Enter the pid of the playlist you want to add the song to: ")
                #check the largest sorder in the playlist and add 1 to it
                
                cursor.execute(
                               '''SELECT * FROM plinclude WHERE pid = {0}'''.format(pid))
                results = cursor.fetchall()
                sorder = len(results) + 1
                cursor.execute('''
                INSERT OR IGNORE INTO plinclude (pid, sid, sorder)
                VALUES ({0}, {1}, {2})
                '''.format(pid, song_choice, sorder))
                connection.commit()
                print("Song added to playlist")
  
#function for artist actions
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
    
    
    def top_3_stats():
          global connection, cursor
          #test aid
          aid = 'a1'
          cursor.execute('''
          SELECT uid, SUM(cnt) FROM listen WHERE sid IN (SELECT sid FROM perform WHERE aid = "{0}") GROUP BY uid ORDER BY SUM(cnt) DESC LIMIT 3
          '''.format(aid))
          results = cursor.fetchall()
          print("Top 3 users based on longest listening time: ")
          for row in results:
              print(row[0], row[1])
          cursor.execute('''
          SELECT pid, COUNT(sid) FROM plinclude WHERE sid IN (SELECT sid FROM perform WHERE aid = "{0}") GROUP BY pid ORDER BY COUNT(sid) DESC LIMIT 3
          '''.format(aid))
          results = cursor.fetchall()
          print("Top 3 playlists based on number of songs in the playlist: ")
          for row in results:
              print(row[0], row[1]) 
          connection.commit()
          
   
    def display_artist_songs():
        aid = 'a1'
        cursor.execute('''
        SELECT * FROM songs WHERE sid IN (SELECT sid FROM perform WHERE aid = "{0}")
        '''.format(aid))
        results = cursor.fetchall()
        print("Songs: ")
        for row in results:
            print(row[0], row[1], row[2], row[3])
        
    add_song()
    #show all songs by the artist
    #top_3_stats()
       
#function for searching for artists
def search_artist():
    global connection, cursor
    
    '''
    -- User provides 1 or more unique keywords 
    -- System retrieves all artists that have any of the given keywords or the songs they perform have any of the given keywords
    -- for each artist, return the artist id, name, nationality, and number of songs performed
    -- results should be ordered based on the number of matching keywords with the artist with the most matches displayed first
    -- user should be able to select an artist and perform an artist_action()
    '''   
    
    def add_artist_total_songs_performed():
        global connection, cursor
        cursor.execute( 'ALTER TABLE {tn} ADD COLUMN {cn} {ct}'\
                .format( tn="artists", cn="total_songs_performed", ct="int" ) )
        connection.commit()
        cursor.execute('''
                    UPDATE artists
                    SET total_songs_performed = (SELECT COUNT(*) FROM perform WHERE perform.aid = artists.aid)
                    ''')
        connection.commit()
    def select_AID(results):
        aid = []
        for i in range(len(results)):
                aid.append(results[i][1][0])
        return aid
    #add_artist_total_songs_performed()
    
    user_input = input("search for artists: ")
  
    #user_input = "love cold fire"
    
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
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    def orderOutput(results):
        output = []
        for i in range(len(results)):
            output.append([0, results[i]])
        for i in range(len(results)):
            for j in range(len(user_input)):
                if user_input[j].lower() in results[i][1].lower():
                    output[i][0] += 1
        output.sort(reverse = True)
        return output
    
    print("Search Results:")
    results = orderOutput(results)
    selectable_AID = select_AID(results)
    
    for i in range(len(results)):
        if i < 5:
            print(results[i][1][0], results[i][1][1], results[i][1][2])
    
    if len(selectable_AID) > 0:
        select_artist(selectable_AID)
   
    
    connection.commit()
 
#function for selecting an artist

def select_artist(results):
    global connection, cursor
    '''
    --given an artist id, return the sid, title, and duration of all the artist's song
    
    '''
    def select_A_SID(results):
        sid = []
        for i in range(len(results)):
                sid.append(results[i][0])
        return sid
    
    aid = input("Enter the aid of the artist you would like to select: ")
    cursor.execute('''
    SELECT sid, title, duration FROM songs WHERE sid IN (SELECT sid FROM perform WHERE aid = "{0}")
    '''.format(aid))
    results = cursor.fetchall()
    selectable_SIDs = select_A_SID(results)
    print("Songs: ")
    for row in results:
        print(row[0], row[1], row[2])
    connection.commit()
    
    print(selectable_SIDs)
    if len(selectable_SIDs) > 0:
        song_action(selectable_SIDs)


#defines tables and inserts data
    
def define_tables():
    global connection, cursor
    
    users_query = '''
    
    create table users (
    uid		char(4),
    name		text,
    primary key (uid)
    );
    
    '''
    
    songs_query = '''
    create table songs (
    sid		int,
    title		text,
    duration	int,
    primary key (sid)
    );
    '''
    sessions_query = '''
    CREATE TABLE sessions (
    uid		char(4),
    sno		int,
    start 	date,
    end 		date,
    primary key (uid,sno),
    foreign key (uid) references users
        on delete cascade
    );
    
    '''
    listen_query = '''
    create table listen (
    uid		char(4),
    sno		int,
    sid		int,
    cnt		real,
    primary key (uid,sno,sid),
    foreign key (uid,sno) references sessions,
    foreign key (sid) references songs
    );
    
    
    '''
    playlists_query = '''
    
    create table playlists (
    pid		int,
    title		text,
    uid		char(4),
    primary key (pid),
    foreign key (uid) references users
    );    
    '''
    plinclude_query = '''
    create table plinclude (
    pid		int,
    sid		int,
    sorder	int,
    primary key (pid,sid),
    foreign key (pid) references playlists,
    foreign key (sid) references songs
    );
    
    
    '''
    artists_query = '''
    
    create table artists (
    aid		char(4),
    name		text,
    nationality	text,
    primary key (aid)
    );
    
    
    '''
    perform_query = '''
    
    create table perform (
    aid		char(4),
    sid		int,
    primary key (aid,sid),
    foreign key (aid) references artists,
    foreign key (sid) references songs
    );
    '''
    
    cursor.execute(users_query)
    cursor.execute(songs_query)
    cursor.execute(sessions_query)
    cursor.execute(listen_query)
    cursor.execute(playlists_query)
    cursor.execute(plinclude_query)
    cursor.execute(artists_query)
    cursor.execute(perform_query)
    connection.commit()
    
def insert_data():
    """ Insert data into the tables """
    global connection, cursor 
    
    insert_users = '''
    
    insert into users values ('u1', 'Maheen Lynn'),
    ('u2', 'Leena Markham'),
    ('u3', 'Branden Escobar'),
    ('u4', 'Digby Tierney'),
    ('u5', 'Harriet Beck'),
    ('u6', 'Aron Gu'),
    ('u7', 'Jeevan Dillard'),
    ('u8', 'Laaibah Cano'),
    ('u9', 'Ameila Pike'),
    ('u10','Davood Rafiei'),
    ('u11', 'Spencer Schimdt'),
    ('u12', 'Ryder Catonio'),
    ('u13', 'Dradelli Guy'),
    ('u14', 'Aron Gu'),
    ('u15', 'Mark Sanchez'),
    ('u16', 'Marion Trap'),
    ('u17', 'Mackenzie Parks'),
    ('u18', 'Daria Blackburn'),
    ('u19', 'Samuel Dixon'),
    ('u20','Hamed Mirzaei'),
    ('u21', 'Amelia Pike'),
    ('u22', 'Quinn Mccartney'),
    ('u23', 'Brenden Akhtar'),
    ('u24', 'Catrina Maxwell'),
    ('u25', 'Darsh Snyder'),
    ('u26', 'Pheobe Shannon'),
    ('u27', 'Judy Walsh'),
    ('u28', 'Bret Bartlett'),
    ('u29', 'Diogo Lowry'),
    ('u30', 'Rudra Duke'),
    ('u31', 'Mike Smith'),
    ('u32', 'Conner Wang'),
    ('u33', 'Saim Hays'),
    ('u34', 'Jeanne Carlson'),
    ('u35', 'John-Paul Whittaker'),
    ('u36', 'Bjorn Partridge'),
    ('u37', 'Dominic Chen'),
    ('u38', 'Aleah Mendoza'),
    ('u39', 'Kiyan Underwood'),
    ('u40', 'Wendy Fernandez'),
    ('u41', 'Shamima Gonzales'),
    ('u42', 'Mike Smith')
        
    '''
    
    insert_songs = '''
    
    insert into songs values (1, 'Waka Waka(This Time For Africa)', 202),
     (2, 'Applause', 212),
     (3, 'Demons', 177),
     (4, 'Counting Stars', 259),
     (5, 'Wavin flag', 220),
     (6, 'Just Give Me a Reason', 242),
     (7, 'Stronger(What Doesn`t Kill You)', 222),
     (8, 'We Are Young', 233),
     (9, 'Moves Like Jagger', 201),
     (10, 'Nice for what', 210),
     (11, 'Hold on, we are going home', 227),
     (12, 'DJ Got Us Fallin` in Love', 221),
     (13, 'Wild Ones', 233),
     (14, 'Everybody Talks', 179),
     (15, 'Good Time', 206),
     (16, 'Blame', 214),
     (17, 'I Need Your Love', 234),
     (18, 'Wake Me Up', 249),
     (19, 'Poker Face', 238),
     (20, 'Cheap Thrills', 224),
     (21, 'No Lie', 221),
     (22, 'Gentleman', 194),
     (23, 'Titanium', 245),
     (24, 'Cool Kids', 237),
     (25, 'Chasing The Sun', 199),
     (26, 'We Found Love', 215),
     (27, 'Give Me Everything', 252),
     (28, 'Come & Get It', 231),
     (29, 'Me and My Broken Heart', 193),
     (30, 'Best Day of My Life', 194),
     (31, 'International Love', 227),
     (32, 'You Make Me Feel...', 216),
     (33, 'Safe and Sound', 193),
     (34, 'Burn', 231),
     (35, 'Shut Up and Dance', 197),
     (36, 'Want to Want Me', 207),
     (37, 'Dynamite', 202),
     (38, 'Feel This Moment', 229),
     (39, 'Hall of Fame', 202),
     (40, 'On the Floor', 231),
     (41, 'I Feel It Coming', 269),
     (42, 'Blinding Lights', 201),
     (43, 'My Heart Will Go On', 280),
     (44, 'I`m Alive', 210),
     (45, 'Complicated', 244),
     (46, 'Club Can`t Handle Me', 232),
     (47, 'Wannabe', 172),
     (48, 'Shape of You', 233);
        
        
    ''' 
    insert_sessions = '''
    --- Sessions ---
-- September 2022
insert into sessions values ('u10', 1, '2022-09-27', '2022-09-28'),
 ('u20', 1, '2022-09-25', '2022-09-27'),
 ('u3', 2, '2022-09-24', '2022-09-25'),
 ('u36', 3, '2022-09-24', '2022-09-25'),
 ('u1', 4, '2022-09-23', '2022-09-27'),
 ('u32', 5, '2022-09-22', '2022-09-24'),
 ('u23', 5, '2022-09-22', '2022-09-23'),
 ('u39', 6, '2022-09-16', '2022-09-18'),
 ('u32', 6, '2022-09-12', '2022-09-21'),
 ('u10', 7, '2022-09-13', '2022-09-16'),
 ('u22', 8, '2022-09-12', '2022-09-14'),
 ('u23', 9, '2022-09-08', '2022-09-15'),
 ('u15', 9, '2022-09-06', '2022-09-09'),
 ('u17', 10, '2022-09-02', '2022-09-04'),

-- August 2022
 ('u3', 10, '2022-08-25', '2022-08-28'),
 ('u7', 10, '2022-08-20', '2022-08-23'),
 ('u41', 11, '2022-08-22', '2022-08-26'),

-- July 2022
 ('u32', 11, '2022-07-19', '2022-07-23'),
 ('u28', 11, '2022-07-01', '2022-07-05'),

-- June 2022
 ('u9', 12, '2022-06-18', '2022-06-22'),
 ('u16', 13, '2022-06-16', '2020-06-18'),
 ('u23', 13, '2022-06-10', '2022-06-13'),

-- May 2022
 ('u26', 14, '2022-05-23', '2022-05-25'),
 ('u29', 14, '2022-05-27', '2022-05-31'),
 ('u35', 15, '2022-05-20', '2022-05-23'),
 ('u23', 15, '2022-05-10', '2022-05-14'),

-- April 2022
 ('u33', 16, '2022-04-28', '2022-04-30'),
 ('u19', 17, '2022-04-15', '2022-04-18'),
 ('u8', 17, '2022-04-02', '2022-04-05'),

-- March 2022
 ('u8', 18, '2022-03-25', '2022-03-28'),
 ('u14', 19, '2022-03-07', '2022-03-11'),

-- February 2022
 ('u1', 20, '2022-02-23', '2022-02-26'),
 ('u5', 20, '2022-02-17', '2022-02-20'),
 ('u9', 20, '2022-02-08', '2022-02-11'),
 ('u11', 20, '2022-02-02', '2022-02-05'),

-- January 2022
 ('u10', 21, '2022-01-28', '2022-01-31'),
 ('u6', 21, '2022-01-25', '2022-01-28'),
 ('u9', 21, '2022-01-22', '2022-01-25'),
 ('u13', 22, '2022-01-19', '2022-01-21'),

-- December 2021
 ('u19', 22, '2021-12-31', '2022-01-02'),
 ('u17', 22, '2021-12-20', '2021-12-25'),
 ('u27', 22, '2021-12-16', '2021-12-20'),

-- November 2021
 ('u11', 23, '2021-11-18', '2021-11-22'),
 ('u4', 23, '2021-11-17', '2021-11-19'),
 ('u42', 23, '2021-11-16', '2021-11-18'),

-- October 2021
 ('u2', 24, '2021-10-30', '2021-11-03'),
 ('u11', 24, '2021-10-27', '2021-10-30'),
 ('u38', 24, '2021-10-24', '2021-10-27'),

-- September 2021
 ('u37', 25, '2021-09-30', '2021-10-02'),
 ('u30', 25, '2021-09-26', '2021-09-29'),
 ('u18', 25, '2021-09-23', '2021-09-25'),
 ('u1', 25, '2021-09-23', '2021-09-24'),
 ('u25', 26, '2021-09-15', '2021-09-19'),
 ('u24', 26, '2021-09-10', '2021-09-14'),
 ('u39', 26, '2021-09-06', '2021-09-10'),

-- August 2021 
 ('u12', 27, '2021-08-31', '2021-09-02'),
 ('u26', 27, '2021-08-25', '2021-08-28'),
 ('u40', 27, '2021-08-23', '2021-08-25'),
 ('u21', 27, '2021-08-15', '2021-08-18'),

-- July 2021
 ('u42', 28, '2021-07-29', '2021-07-31'),
 ('u34', 29, '2021-07-15', '2021-07-20'),
 ('u31', 29, '2021-07-12', '2021-07-13'),

-- June 2021 
 ('u13', 30, '2021-06-24', '2021-06-28'),

-- May 2021
 ('u18', 31, '2021-05-30', '2021-06-01'),
 ('u18', 32, '2021-05-23', '2021-05-26'),
 ('u19', 32, '2021-05-18', '2021-05-21'),

-- April 2021
 ('u41', 33, '2021-04-28', '2021-04-30'),
 ('u7', 33, '2021-04-25', '2021-04-26'),
 ('u14', 33, '2021-04-19', '2021-04-23'),
 ('u16', 34, '2021-04-15', '2021-04-17'),

-- March 2021
 ('u6', 35, '2021-03-30', '2021-04-01'),
 ('u17', 35, '2021-03-27', '2021-03-28'), 
 ('u24', 36, '2021-03-24', '2021-03-26'),
 ('u22', 36, '2021-03-21', '2021-03-24'),

-- February 2021
 ('u29', 37, '2021-02-28', '2021-03-02'),
 ('u37', 37, '2021-02-25', '2021-02-26'),
 ('u12', 38, '2021-02-19', '2021-02-25'),
 ('u38', 38, '2021-02-15', '2021-02-18'),

-- January 2021
 ('u7', 39, '2021-01-26', '2021-01-29'),
 ('u25', 39, '2021-01-23', '2021-01-25'),
 ('u32', 39, '2021-01-23', '2021-01-25'),
 ('u42', 40, '2021-01-15', '2021-01-18'),
 ('u5', 40, '2021-01-01', '2021-01-06');

    
    
    '''
     
    insert_listen = '''


--- Listen ---
-- September 2022 --
-- Session 1 (11 unique songs)
insert into listen values ('u10', 1, 5, 1.2),
 ('u10', 1, 11, 2.0),
 ('u10', 1, 40, 33),
 ('u10', 1, 25, 14),
 ('u10', 1, 13, 22),
 ('u10', 1, 35, 21),
 ('u20', 1, 23, 3.2),
 ('u20', 1, 12, 45),
 ('u20', 1, 43, 32),
 ('u20', 1, 5, 44),
 ('u20', 1, 6, 32),
 ('u20', 1, 42, 0.9),

-- Session 2 (4 unique songs)
 ('u3', 2, 42, 9.7),
 ('u3', 2, 30, 11.8),
 ('u3', 2, 14, 23.4),
 ('u3', 2, 10, 33.2),

-- Session 3 (3 unique songs)
 ('u36', 3, 25, 1000),
 ('u36', 3, 42, 53.6),
 ('u36', 3, 9, 43),

-- Session 4 (3 unique songs)
 ('u1', 4, 2, 3),
 ('u1', 4, 12, 5),
 ('u1', 4, 16, 4),

-- Session 5 (7 unique songs)
 ('u23', 5, 45, 70.3),
 ('u23', 5, 33, 67.5),
 ('u23', 5, 15, 81),
 ('u32', 5, 42, 4.3),
 ('u32', 5, 27, 5.5),
 ('u32', 5, 16, 6.4),
 ('u32', 5, 5, 4.4),

-- Session 6 (9 unique songs)
 ('u32', 6, 20, 123),
 ('u32', 6, 42, 11.2),
 ('u32', 6, 5, 7.6),
 ('u39', 6, 29, 2.5),
 ('u39', 6, 12, 43),
 ('u39', 6, 6, 6),
 ('u39', 6, 34, 31),
 ('u39', 6, 11, 43),
 ('u39', 6, 7, 6),

-- Session 7 (4 unique songs)
 ('u10', 7, 13, 22),
 ('u10', 7, 25, 10),
 ('u10', 7, 42, 23.3),
 ('u10', 7, 33, 32.5),

-- Session 8 (1 unique song)
 ('u22', 8, 40, 23.1),

-- Session 9 (5 unique songs)
 ('u15', 9, 42, 29.9),
 ('u15', 9, 32, 10.3),
 ('u23', 9, 43, 32),
 ('u23', 9, 31, 29),
 ('u15', 9, 22, 15),

-- Session 10 (6 unique songs)
 ('u3', 10, 16, 0.5),
 ('u3', 10, 30, 14.7),
 ('u17', 10, 30, 10.3),

-- August 2022 --
 ('u7', 10, 38, 4.4),
 ('u7', 10, 23, 14.2),
 ('u7', 10, 27, 39),
 ('u7', 10, 42, 22),
 ('u3', 10, 38, 6.7),
 ('u3', 10, 23, 14.4),
 ('u3', 10, 42, 15.6),

-- Session 11 (3 unique songs)
 ('u41', 11, 36, 22.6),
 ('u41', 11, 41, 0.3),
 ('u41', 11, 38, 5),

-- June 2022 --
-- Session 12 (7 unique songs)
 ('u9', 12, 43, 44.3),
 ('u9', 12, 26, 25),
 ('u9', 12, 16, 29),
 ('u9', 12, 36, 25),
 ('u9', 12, 21, 20),
 ('u9', 12, 37, 22),
 ('u9', 12, 41, 22),

-- Session 13 (6 unique songs)
 ('u16', 13, 41, 33),
 ('u16', 13, 36, 12),
 ('u16', 13, 21, 21),
 ('u16', 13, 37, 23),
 ('u23', 13, 3, 10.4),
 ('u23', 13, 10, 105.7),
 ('u23', 13, 21, 12),
 ('u23', 13, 36, 11),
 ('u23', 13, 37, 20),
 ('u23', 13, 41, 11),

-- May 2022 --
-- Session 14 (7 unique songs)
 ('u26', 14, 44, 32.2),
 ('u26', 14, 34, 22),
 ('u26', 14, 26, 20),
 ('u29', 14, 45, 8.5),
 ('u29', 14, 44, 23),
 ('u29', 14, 23, 33),
 ('u29', 14, 7, 7),
 ('u29', 14, 8, 5),

-- Session 15 (10 unique songs)
 ('u35', 15, 45, 54),
 ('u35', 15, 32, 29),
 ('u35', 15, 44, 20),
 ('u35', 15, 5, 5.3),
 ('u35', 15, 4, 32),
 ('u23', 15, 1, 15),
 ('u23', 15, 8, 4.9),
 ('u23', 15, 44, 23),
 ('u23', 15, 19, 19),
 ('u23', 15, 3, 5),

-- April 2022 --
-- Session 16 (3 unique songs)
 ('u33', 16, 5, 11),
 ('u33', 16, 44, 5.5),
 ('u33', 16, 20, 11),

-- Session 17 (12 unique songs)
 ('u19', 17, 32, 9.9),
 ('u19', 17, 5, 10),
 ('u19', 17, 20, 10.1),
 ('u19', 17, 19, 15),
 ('u19', 17, 14, 8),
 ('u8', 17, 20, 12.2),
 ('u8', 17, 3, 62.3),
 ('u8', 17, 31, 2.3),
 ('u8', 17, 38, 5.5),
 ('u8', 17, 40, 4.5),
 ('u8', 17, 26, 12),
 ('u8', 17, 24, 8.8),
 ('u8', 17, 39, 10),

-- March 2022 --
-- Session 18 (2 unique songs)
 ('u8', 18, 24, 3.3),
 ('u8', 18, 38, 12.5),

-- Session 19 (7 unique songs)
 ('u14', 19, 32, 5.5),
 ('u14', 19, 35, 5.5),
 ('u14', 19, 29, 5.5),
 ('u14', 19, 16, 5.5),
 ('u14', 19, 17, 3.1),
 ('u14', 19, 34, 2.4),
 ('u14', 19, 23, 5.5),

-- February 2022 --
-- Session 20 (3 unique songs)
 ('u1', 20, 20, 20),
 ('u1', 20, 21, 23),
 ('u1', 20, 6, 18),

-- January 2022 --
-- Session 21 (6 unique songs)
 ('u10', 21, 25, 9),
 ('u10', 21, 13, 0.9),
 ('u10', 21, 40, 12),
 ('u6', 21, 43, 10),
 ('u6', 21, 4, 6),
 ('u6', 21, 5, 11),
 ('u6', 21, 40, 22),
 ('u9', 21, 40, 12),
 ('u9', 21, 5, 6),
 ('u9', 21, 43, 5),

-- December 2021 --
-- Session 22 (10 unique songs)
 ('u13', 22, 40, 4),
 ('u13', 22, 5, 5),
 ('u17', 22, 18, 5),
 ('u17', 22, 34, 6),
 ('u17', 22, 17, 4),
 ('u17', 22, 20, 6),
 ('u17', 22, 21, 8),
 ('u17', 22, 16, 5.4),
 ('u27', 22, 9, 32),
 ('u27', 22, 7, 21),
 ('u27', 22, 14, 6),

-- November 2021 --
-- Session 23 (2 unique songs)
 ('u11', 23, 11, 21.5),
 ('u11', 23, 29, 44),
 ('u4', 23, 29, 10),
 ('u4', 23, 11, 20),
 ('u42', 23, 29, 10),
 ('u42', 23, 11, 15),

-- October 2021 --
-- Session 24 (12 unique songs)
 ('u2', 24, 1, 5),
 ('u2', 24, 8, 8.4),
 ('u2', 24, 12, 3.3),
 ('u2', 24, 17, 125.4),
 ('u2', 24, 2, 63.8),
 ('u2', 24, 7, 34.2),
 ('u2', 24, 36, 12.7),
 ('u2', 24, 37, 19.5),
 ('u2', 24, 35, 10.7),
 ('u11', 24, 2, 13.4),
 ('u11', 24, 43, 102.2),
 ('u11', 24, 9, 9),
 ('u11', 24, 8, 14.5),
 ('u11', 24, 22, 22),
 ('u38', 24, 19, 6),
 ('u38', 24, 33, 19.3),
 ('u38', 24, 2, 10.5),
 ('u38', 24, 8, 20.4),

-- September 2021 --
-- Session 25 (13 unique songs)
 ('u37', 25, 25, 2.6),
 ('u37', 25, 35, 10.6),
 ('u37', 25, 17, 39.4),
 ('u37', 25, 31, 19.2),
 ('u37', 25, 29, 18),
 ('u37', 25, 28, 19),
 ('u30', 25, 17, 20),
 ('u30', 25, 44, 19.3),
 ('u30', 25, 34, 43),
 ('u30', 25, 5, 5),
 ('u30', 25, 29, 11),
 ('u18', 25, 1, 12.7),
 ('u18', 25, 26, 26.8),
 ('u18', 25, 17, 23.4),
 ('u18', 25, 21, 32),
 ('u1', 25, 44, 63.9),
 ('u1', 25, 17, 33.8),
 ('u1', 25, 23, 26.5),
 ('u1', 25, 29, 39.5),

-- Session 26 (10 unique songs)
 ('u25', 26, 44, 32.6),
 ('u25', 26, 17, 40.5),
 ('u25', 26, 6, 6.5),
 ('u25', 26, 10, 10.9),
 ('u25', 26, 18, 23),
 ('u24', 26, 44, 39.2),
 ('u24', 26, 17, 54.8),
 ('u24', 26, 35, 30.4),
 ('u24', 26, 36, 23.6),
 ('u24', 26, 28, 55.5),
 ('u39', 26, 44, 26.8),
 ('u39', 26, 17, 17.9),
 ('u39', 26, 29, 43.7),
 ('u39', 26, 28, 71.4),
 ('u39', 26, 27, 55),

-- August 2021 --
-- Session 27 (8 unique songs)
 ('u12', 27, 41, 32),
 ('u12', 27, 23, 5),
 ('u12', 27, 10, 29),
 ('u12', 27, 16, 5),
 ('u26', 27, 16, 5),
 ('u26', 27, 18, 5.6),
 ('u26', 27, 41, 23.2),
 ('u40', 27, 17, 32),
 ('u40', 27, 23, 12),
 ('u40', 27, 7, 12.5),
 ('u21', 27, 41, 45.2),
 ('u21', 27, 16, 32.6),
 ('u21', 27, 32, 5.3),

-- July 2021 --
-- Session 28 (3 unique songs)
 ('u42', 28, 33, 33.3),
 ('u42', 28, 25, 19),
 ('u42', 28, 8, 8.6),

-- Session 29 (4 unique songs)
 ('u34', 29, 8, 5.1),
 ('u34', 29, 9, 9.7),
 ('u34', 29, 33, 21.4),
 ('u31', 29, 33, 15.6),
 ('u31', 29, 8, 4.3),
 ('u31', 29, 15, 3.5),

-- June 2021 --
-- Session 30 (5 unique songs)
 ('u13', 30, 14, 5.6),
 ('u13', 30, 4, 6.7),
 ('u13', 30, 6, 5),
 ('u13', 30, 27, 30),
 ('u13', 30, 47, 16),

-- May 2021 --
-- Session 31 (2 unique songs)
 ('u18', 31, 32, 43.2),
 ('u18', 31, 26, 129.5),

-- Session 32 (2 unique songs)
 ('u18', 32, 26, 45.7),
 ('u18', 32, 24, 24.6),
 ('u19', 32, 24, 34.2),
 ('u19', 32, 26, 45),

-- April 2021 --
-- Session 33 (2 unique songs)
 ('u41', 33, 37, 43.2),
 ('u41', 33, 15, 32),
 ('u7', 33, 15, 32.2),
 ('u7', 33, 37, 28.44),
 ('u14', 33, 15, 98.34),
 ('u14', 33, 37, 46.65),

-- Session 34 (4 unique songs)
 ('u16', 34, 26, 37.32),
 ('u16', 34, 37, 15.89),
 ('u16', 34, 15, 18.99),
 ('u16', 34, 47, 16),

-- March 2021 --
-- Session 35 (3 unique songs)
 ('u6', 35, 32, 12.5),
 ('u6', 35, 11, 11.29),
 ('u17', 35, 15, 11.83),
 ('u17', 35, 32, 101.22),
 ('u17', 35, 11, 182.38),

-- Session 36 (4 unique songs)
 ('u24', 36, 42, 23.5),
 ('u24', 36, 11, 32.5),
 ('u24', 36, 15, 23.55),
 ('u24', 36, 32, 21.3),
 ('u22', 36, 42, 83.46),
 ('u22', 36, 11, 29.99),
 ('u22', 36, 15, 12.43),
 ('u22', 36, 32, 111.11),

-- February 2021 --
-- Session 37 (4 unique songs)
 ('u29', 37, 39, 12.97),
 ('u29', 37, 12, 12.77),
 ('u29', 37, 40, 49),
 ('u37', 37, 36, 125),
 ('u37', 37, 12, 33.36),

-- Session 38 (2 unique songs)
 ('u12', 38, 25, 32.55),
 ('u12', 38, 40, 281),
 ('u38', 38, 25, 286.21),

-- January 2021 --
-- Session 39 (1 unique song)
 ('u7', 39, 4, 251),
 ('u25', 39, 4, 345.32),
 ('u32', 39, 4, 501),

-- Session 40 (8 unique songs)
 ('u42', 40, 4, 104.18),
 ('u42', 40, 9, 23),
 ('u42', 40, 6, 24),
 ('u42', 40, 43, 15),
 ('u42', 40, 3, 14),
 ('u42', 40, 41, 41.2),
 ('u42', 40, 18, 19.91),
 ('u5', 40, 3, 10),
 ('u5', 40, 4, 111),
 ('u5', 40, 38, 12.23),
 ('u5', 40, 6, 23.35);

'''

    insert_playlists = '''

--- Playlists ---
insert into playlists values (1, 'Fun Songs', 'u25'),
 (2, 'Relaxing Music', 'u40'),
 (3, 'Relaxing Music', 'u25'),
 (4, '2010s', 'u36'),
 (5, 'Pop Music', 'u7'),
 (6, 'Obscene Language', 'u11'),
 (7, 'Yolo', 'u13'),
 (8, 'Favorites', 'u22'),
 (9, 'Favorites', 'u22'),
 (10, 'Wouldn`t Play Again', 'u33'),
 (11, 'Fun Songs', 'u9'),
 (12, 'Love These Songs!', 'u34'),
 (13, 'Retro Music', 'u22'),
 (14, 'Trending Songs', 'u19'),
 (15, 'Castle Music', 'u6'),
 (16, 'Lady Gaga', 'u17'),
 (17, 'Sean Paul', 'u19'),
 (18, 'Rap', 'u38'),
 (19, 'Pop Music', 'u31'),
 (20, 'Let`s Get It!', 'u3'),
 (21, 'Funny Songs', 'u27'),
 (22, 'Great', 'u24'),
 (23, '2013 Songs', 'u26'),
 (24, '3 Minute Songs', 'u42'),
 (25, '30', 'u28'),
 (26, 'Whoa', 'u9'),
 (27, 'Lol', 'u15'),
 (28, 'Davood`s Favorites', 'u10'),
 (29, 'Ryder`s Favorites', 'u12'),
 (30, 'Songs for 291', 'u10'),
 (31, 'Cool Playlist', 'u18');



'''

    insert_plincludes = '''

--- PlInclude ---
-- Playlist 1
insert into plinclude values (1, 35, 1),
 (1, 24, 3),
 (1, 9, 2),
 (1, 42, 4),
 (1, 25, 5),

-- Playlist 2
 (2, 8, 1),
 (2, 5, 2),
 (2, 15, 3),
 (2, 17, 4),
 (2, 19, 5),
 (2, 39, 6),

-- Playlist 3
 (3, 5, 1),
 (3, 42, 2),
 (3, 43, 3),
 (3, 4, 4),
 (3, 13, 5),
 (3, 40, 6),

-- Playlist 4
 (4, 26, 1),
 (4, 19, 2),
 (4, 3, 3),

-- Playlist 5
 (5, 11, 1),
 (5, 29, 2),
 (5, 34, 3),
 (5, 44, 4),

-- Playlist 6
 (6, 42, 1),
 (6, 23, 2),
 (6, 12, 3),
 (6, 2, 4),
 (6, 11, 5),
 (6, 35, 6),
 (6, 25, 7),
 (6, 6, 8),
 (6, 33, 9),

-- Playlist 7
 (7, 31, 1),
 (7, 22, 2),
 (7, 13, 3),
 (7, 45, 5),
 (7, 27, 4),

-- Playlist 8
 (8, 25, 1),
 (8, 11, 2),

-- Playlist 9
 (9, 41, 1),
 (9, 23, 2),
 (9, 16, 3),
 (9, 32, 4),
 (9, 10, 5),
 (9, 18, 6),
 (9, 25, 7),
 (9, 33, 8),
 (9, 8, 9),
 (9, 9, 10),

-- Playlist 10
 (10, 39, 1),
 (10, 40, 2),
 (10, 36, 3),
 (10, 26, 4),
 (10, 11, 5),
 (10, 42, 6),
 (10, 15, 7),

-- Playlist 11
 (11, 8, 1),
 (11, 15, 2),
 (11, 13, 3),
 (11, 44, 4),
 (11, 20, 5),
 (11, 5, 6),
 (11, 27, 7),
 (11, 16, 8),
 (11, 38, 9),
 (11, 30, 10),
 (11, 23, 11),

-- Playlist 12
 (12, 28, 1),
 (12, 20, 2),
 (12, 43, 3),

-- Playlist 14
 (14, 39, 1),
 (14, 20, 2),
 (14, 24, 3),
 (14, 27, 4),

-- Playlist 15
 (15, 10, 1),
 (15, 2, 2),
 (15, 35, 3),

-- Playlist 16
 (16, 2, 1),
 (16, 13, 2),
 (16, 10, 3),
 (16, 14, 4),
 (16, 9, 5),
 (16, 29, 6),
 (16, 33, 7),
 (16, 20, 8),
 (16, 1, 9),
 (16, 40, 10),

-- Playlist 17
 (17, 45, 1),
 (17, 35, 2),
 (17, 17, 3),
 (17, 31, 4),
 (17, 29, 5),
 (17, 44, 6),
 (17, 34, 7),
 (17, 1, 8),
 (17, 26, 9),
 (17, 23, 10),
 (17, 8, 11),
 (17, 2, 12),
 (17, 43, 13),
 (17, 36, 14),
 (17, 37, 15),
 (17, 22, 16),
 (17, 7, 17),

-- Playlist 18
 (18, 44, 1),
 (18, 41, 2),

-- Playlist 19
 (19, 40, 1),
 (19, 16, 2),
 (19, 18, 3),
 (19, 5, 4),
 (19, 9, 5),
 (19, 7, 6),
 (19, 20, 7),

-- Playlist 20
 (20, 8, 1),
 (20, 2, 2),
 (20, 6, 3),

-- Playlist 21
 (21, 1, 1),
 (21, 2, 2),
 (21, 3, 3),
 (21, 4, 4),
 (21, 5, 5),
 (21, 6, 6),
 (21, 7, 7),
 (21, 8, 8),
 (21, 9, 9),
 (21, 10, 10),
 (21, 11, 11),
 (21, 12, 12),
 (21, 13, 13),
 (21, 14, 14),
 (21, 15, 15),
 (21, 16, 16),
 (21, 17, 17),
 (21, 18, 18),
 (21, 19, 19),
 (21, 20, 20),
 (21, 21, 21),
 (21, 22, 22),
 (21, 23, 23),
 (21, 24, 24),
 (21, 25, 25),
 (21, 26, 26),
 (21, 27, 27),
 (21, 28, 28),
 (21, 29, 29),
 (21, 30, 30),
 (21, 31, 31),
 (21, 32, 32),
 (21, 33, 33),
 (21, 34, 34),
 (21, 35, 35),
 (21, 36, 36),
 (21, 37, 37),
 (21, 38, 38),
 (21, 39, 39),
 (21, 40, 40),
 (21, 41, 41),
 (21, 42, 42),
 (21, 43, 43),
 (21, 44, 44),
 (21, 45, 45),

-- Playlist 22
 (22, 45, 1),
 (22, 28, 2),

-- Playlist 23
 (23, 9, 1),
 (23, 18, 2),

-- Playlist 24
 (24, 38, 1),

-- Playlist 25
 (25, 32, 1),
 (25, 22, 2),
 (25, 31, 3),
 (25, 43, 4),
 (25, 33, 5),
 (25, 25, 6),
 (25, 8, 7),

-- Playlist 26
 (26, 10, 1),
 (26, 9, 2),
 (26, 8, 3),
 (26, 7, 4),

-- Playlist 27
 (27, 16, 1),
 (27, 5, 2),
 (27, 4, 3),
 (27, 41, 4),
 (27, 12, 5),
 (27, 23, 6),

-- Playlist 28
 (28, 20, 1),
 (28, 21, 2),
 (28, 46, 3),

-- Playlist 29
 (29, 1, 1),
 (29, 8, 2),
 (29, 19, 3),
 (29, 15, 4),
 (29, 14, 5),

-- Playlist 30
 (30, 10, 1),
 (30, 11, 2),
 (30, 20, 3),
 (30, 6, 4),
 (30, 5, 5),
 (30, 19, 6),
 (30, 28, 7),
 (30, 39, 8),
 (30, 15, 9),
 (30, 24, 10),
 (30, 33, 11),
 (30, 22, 12),
 (30, 32, 13),
 (30, 44, 14),
 (30, 36, 15),
 (30, 18, 16),
 (30, 3, 17),
 (30, 42, 18),
 (30, 25, 19),
 (30, 41, 20),
 (30, 35, 21),
 (30, 14, 22),
 (30, 38, 23),

-- Playlist 31
 (31, 5, 1),
 (31, 11, 2),
 (31, 42, 3),
 (31, 6, 4),
 (31, 43, 5),
 (31, 23, 6),
 (31, 12, 7),
 (31, 25, 8),
 (31, 16, 9),
 (31, 46, 10);


'''

    insert_artists = '''

insert into artists values ('a1', 'Lady Gaga', 'United States'),
 ('a2', 'OneRepublic', 'United States'),
 ('a3', 'Imagine Dragons', 'United States'),
 ('a4', 'PSY', 'South Korea'),
 ('a5', 'P!nk', 'American'),
 ('a6', 'Nate Reuss', 'American'),
 ('a7', 'Kelly Clarkson', 'United States'),
 ('a8', 'Janelle Monáe', 'United States'),
 ('a9', 'Maroon 5', 'United States'),
 ('a10', 'Drake', 'Canada'),
 ('a11', 'Pitbull', 'American'),
 ('a12', 'Sia', 'Australian'),
 ('a13', 'Neon Trees', 'American'),
 ('a14', 'Carly Rae Jepsen', 'Canada'),
 ('a15', 'Calvin Harris', 'Scotland'),
 ('a16', 'Ellie Goulding', 'United Kingdom'),
 ('a17', 'Avicii', 'Swedish'),
 ('a18', 'Sean Paul', 'Jamaica'),
 ('a19', 'David Guetta', 'French'),
 ('a20', 'Bob Ezrin', 'Canadian'),
 ('a21', 'Echosmith', 'American'),
 ('a22', 'The Wanted', 'British'),
 ('a23', 'Selena Gomez', 'United States'),
 ('a24', 'Rixton', 'British'),
 ('a25', 'American Authors', 'American'),
 ('a26', 'Cobra Starship', 'American'),
 ('a27', 'Captial Cities', 'American'),
 ('a28', 'WALK THE MOON', 'United States'),
 ('a29', 'Jason Derulo', 'American'),
 ('a30', 'Taio Cruz', 'English'),
 ('a31', 'The Script', 'Ireland'),
 ('a32', 'Jennifer Lopez', 'American'),
 ('a33', 'Shakira', 'Colombia'),
 ('a34', 'The Weeknd', 'Canada'),
 ('a35', 'Celine Dion', 'Canada'),
 ('a36', 'Avril Lavigne', 'Canadian'),
 ('a37', 'Flo Rida', 'American'),
 ('a38', 'Spice Girls', 'British'),
 ('a39', 'Ed Sheeran', 'England');



'''

    insert_perform = '''

insert into perform values ('a1', 2),
 ('a1', 19),
 ('a2', 4),
 ('a3', 3),
 ('a4', 22),
 ('a5', 6),
 ('a6', 6),
 ('a7', 7),
 ('a8', 8),
 ('a9', 9),
 ('a10', 5),
 ('a11', 12),
 ('a11', 27),
 ('a11', 31),
 ('a11', 38),
 ('a11', 40),
 ('a12', 13),
 ('a12', 20),
 ('a12', 23),
 ('a13', 14),
 ('a14', 15),
 ('a15', 16),
 ('a15', 17),
 ('a15', 26),
 ('a16', 17),
 ('a16', 34),
 ('a17', 18),
 ('a18', 20),
 ('a18', 21),
 ('a19', 23),
 ('a19', 46),
 ('a20', 10),
 ('a20', 11),
 ('a21', 24),
 ('a22', 25),
 ('a23', 28),
 ('a24', 29),
 ('a25', 30),
 ('a26', 32),
 ('a27', 33),
 ('a28', 35),
 ('a29', 36),
 ('a30', 37),
 ('a31', 39),
 ('a32', 40),
 ('a33', 1),
 ('a34', 41),
 ('a34', 42),
 ('a35', 43),
 ('a35', 44),
 ('a36', 45),
 ('a37', 46),
 ('a38', 47),
 ('a39', 48);



'''

    # cursor.execute(insert_users)
    cursor.execute(insert_songs)
    cursor.execute(insert_sessions)
    cursor.execute(insert_listen)
    cursor.execute(insert_playlists)
    cursor.execute(insert_plincludes)
    cursor.execute(insert_artists)
    cursor.execute(insert_perform)
    connection.commit()
   

main()