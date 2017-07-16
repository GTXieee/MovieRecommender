import requests
import sqlite3
import math
from tkinter import *
from functools import partial



class Application(Frame):
    """ The window. """
    def __init__(self, master):
        super(Application, self).__init__(master)
        self.grid()
        self.create_widgets()
        self.first_time = True
        self.lang_var = StringVar()
        self.lang_var.set("All") # initial value


    def create_widgets(self):
         Button(self,
                text = "Recommend Movie",
                command = self.recommend,
                ).grid(row = 0, column = 0, columnspan = 1)

         # create labels
         self.movie_labels = []
         for i in range(5):
             i += 1
             movie_label = Label(self,
             text = "Movie" + str(i))
             self.movie_labels.append(movie_label)
             movie_label.grid(row = i, column = 0)

         # seen buttons
         self.buttons = []
         for i in range (5):
             i += 1
             button = Button(self,
                    text = "Seen",
                    command = None)
             self.buttons.append(button)
             button.grid(row = i, column = 1, sticky = E)





    def recommend(self):
        # initiate connection and cursor with watchlist (movies marked as seen from Kodi)
        self.conn_dl = sqlite3.connect('watchedlist.db')
        self.cur_dl = self.conn_dl.cursor()

        # initiate connection and cursor with allwatchedmovies (definitive list which can be changed by user)
        self.conn_awm = sqlite3.connect('allwatchedmovies.db')
        self.cur_awm = self.conn_awm.cursor()

        # create dictionaries
        genredict = {'Action':0, 'Adventure':0, 'Animation':0, 'Biography':0, 'Comedy':0,
                     'Crime':0, 'Documentary':0, 'Drama':0, 'Family':0, 'Fantasy':0,
                     'Film-Noir':0, 'Game-Show':0, 'History':0, 'Horror':0, 'Music':0,
                     'Musical':0, 'Mystery':0, 'News':0, 'Reality-TV':0, 'Romance':0,
                     'Sci-Fi':0, 'Sport':0, 'Talk-Show':0, 'Thriller':0, 'War':0, 'Western':0}
        directordict = dict()

        self.create_table()

        # result = all data from movie_watched table in Kodi-made db
        self.cur_dl.execute('SELECT * FROM movie_watched')
        result = self.cur_dl.fetchall()

        # idcolumn = all data from the imdb_id column in Movies table from awm db
        self.cur_awm.execute('SELECT imdb_id FROM Movies')
        idcolumn = self.cur_awm.fetchall()

        # iterates through each new id from the Kodi-made db & adds it to the awm db
        # with relevant information
        for row in result:
            id = str(row[0])
            new_id = self.idConverter(id)
            idcheck = (int(id),)
            if idcheck in idcolumn: continue

            self.omdb_to_awm(new_id)

        # genrescolumn = genre column from awm db
        self.cur_awm.execute('SELECT genres FROM Movies')
        genrescolumn = self.cur_awm.fetchall()

        # directorcolumn = director column from awm db
        self.cur_awm.execute('SELECT director FROM Movies')
        directorcolumn = self.cur_awm.fetchall()

        # splits up the genres and +1 to the genre-dictionary for each
        for row in genrescolumn:
            row = row[0].split(',')
            for i in row:
                i = i.strip()
                genredict[i] += 1

        # splits up the directors and +1 to the director-dictionary for each
        for row in directorcolumn:
            try:
                row = row[0].split(',')
                for i in row:
                    i = i.strip()
                    directordict[i] = directordict.get(i,0) + 1
            except: directordict[row[0]] = directordict.get(row[0],0) + 1

        # set own weighting for each Genre i.e. based on how common the movies are
        # and human intuition. can't soley base on how common, since there are many
        # more dramas in iMDB top 1,000 than there are comedies.
        wdict1 = {'Action':1.0, 'Adventure':1.0, 'Animation':2.0, 'Biography':2.0, 'Comedy':0.8,
                'Crime':1.0, 'Documentary':5.0, 'Drama':0.7, 'Family':2.0, 'Fantasy':2.0,
                'Film-Noir':4.0, 'Game-Show':1.0, 'History':3.0, 'Horror':4.0, 'Music':4.0,
                'Musical':4.0, 'Mystery':2.0, 'News':1.0, 'Reality-TV':1.0, 'Romance':1.5,
                'Sci-Fi':2.0, 'Sport':4.0, 'Talk-Show':1.0, 'Thriller':1.2, 'War':2.5, 'Western':6.0}

        # create dictionary based on weighting * genre frequency
        wdict2 = wdict1.copy()
        for k,v in wdict2.items():
            wdict2[k] = v * genredict[k]

        #       Algorithm
        # connect and create cursor for top 1,000 movies db
        self.conn_mdb = sqlite3.connect('booleantopmovies.db')
        self.cur_mdb = self.conn_mdb.cursor()

        # allmovies = all data for top 1,000 movies
        self.cur_mdb.execute('SELECT * FROM GenresB')
        allmovies = self.cur_mdb.fetchall()

        # watched_movies = all data from allwatchedmovies
        self.cur_awm.execute('SELECT imdb_id FROM Movies')
        watched_movies = self.cur_awm.fetchall()

        # each un-seen movie from top 1,000 gets designated a score based on
        # similarity to watched movies
        self.languages = {}
        scores = []
        for row in allmovies:
            idcheck2 = (row[0],)
            if (idcheck2) in watched_movies: continue
            genrecount = 0
            for i in row[2:28]:
                genrecount += i
            gscore = (wdict2['Action'] * row[2] +
                         wdict2['Adventure'] * row[3] +
                         wdict2['Animation'] * row[4] +
                         wdict2['Biography'] * row[5] +
                         wdict2['Comedy'] * row[6] +
                         wdict2['Crime'] * row[7] +
                         wdict2['Documentary'] * row[8] +
                         wdict2['Drama'] * row[9] +
                         wdict2['Family'] * row[10] +
                         wdict2['Fantasy'] * row[11] +
                         wdict2['Film-Noir'] * row[12] +
                         wdict2['Game-Show'] * row[13] +
                         wdict2['History'] * row[14] +
                         wdict2['Horror'] * row[15] +
                         wdict2['Music'] * row[16] +
                         wdict2['Musical'] * row[17] +
                         wdict2['Mystery'] * row[18] +
                         wdict2['News'] * row[19] +
                         wdict2['Reality-TV'] * row[20] +
                         wdict2['Romance'] * row[21] +
                         wdict2['Sci-Fi'] * row[22] +
                         wdict2['Sport'] * row[23] +
                         wdict2['Talk-Show'] * row[24] +
                         wdict2['Thriller'] * row[25] +
                         wdict2['War'] * row[26] +
                         wdict2['Western'] * row[27])
            dscore = 0
            try:
                directors = row[28].split(',')
                for d in directors:
                    d = d.strip()
                    if d in directordict.keys(): dscore += directordict[d] * 3
            except:
                director = row[28]
                print(director)
                if director in directordict.keys(): dscore += directordict[directors] * 3

            # language
            language = row[29]
            try:
                languages = language.split(',')
                #for l in languages:
                #    l = l.strip()
                #    self.languages[l] = self.languages.get(l,0) + 1
                primary_language = languages[0].strip()
                self.languages[primary_language] = self.languages.get(primary_language,0) + 1

            except:
                primary_language = language
                self.languages[primary_language] = self.languages.get(primary_language,0) + 1



            # offset the fact that movies labeled with more genres automatically
            # get a higher score with the log function
            gscore = (gscore/genrecount) * math.log(genrecount + 10)
            score = 0.9 * gscore + dscore
            # (title, score, imdb_id)
            scores.append( (row[1], score, row[0], primary_language) )

        language_choice = self.lang_var.get()
        if language_choice != "All":
            scores = filter(lambda x: language_choice in x[3], scores)
        ordered = sorted(scores, key=lambda movie: movie[1], reverse = True)

        try:
            top5 = ordered[:5]
        except:
            top5 = ordered

        self.top5 = top5
        self.disp_top_5()


    def seen(self, movie):
        """ Adds movie to awm db and reloads the list ."""
        print("SEEN")
        imdb_id = self.top5[movie][2]
        imdb_id = self.idConverter(str(imdb_id))

        self.omdb_to_awm(imdb_id)

        self.recommend()

    def omdb_to_awm(self, id):
        """ Adds movie to awm db. """
        url = "http://www.omdbapi.com/?i=" + id + "&plot=short&r=json"
        print(url)

        uh = requests.get(url)
        info = uh.json()

        title = info['Title']
        genre = info['Genre']
        director = info['Director']
        rating = info['imdbRating']
        year = info['Year']
        imdb_id = int(id[2:])
        print(int(id[2:]))

        self.cur_awm.execute('''INSERT OR REPLACE INTO Movies
            (imdb_id, title, genres, director, rating, year)
            VALUES ( ?, ?, ?, ?, ?, ? )''',
            ( imdb_id, title, genre, director, rating, year ) )

        self.conn_awm.commit()


    def idConverter(self, id):
        """ Converts from just numbers to add the 'tt' """
        new_id = "tt" + (7-len(id)) * "0" + id
        return new_id

    def create_table(self):
        """ Creates the table for the awm db. """
        self.cur_awm.executescript('''

        CREATE TABLE IF NOT EXISTS Movies (
            imdb_id  INTEGER PRIMARY KEY UNIQUE,
            title TEXT,
            genres TEXT,
            director TEXT,
            year INTEGER, rating INTEGER
        );
        ''')

    def disp_top_5(self):
        """ Changes the labels to the top 5 results. """
        i = 0
        for movie_label in self.movie_labels:
            try:
                movie_label['text'] = self.top5[i][0]
                i += 1
            except:
                movie_label['text'] = ""

        if self.first_time:
            i = 0
            for button in self.buttons:
                button['command'] = partial(self.seen, i)
                i += 1
            self.first_time = False

            # create language options
            ALL = ["All"]
            language_options = ALL + sorted(self.languages)
            OptionMenu(self, self.lang_var, *language_options
            ).grid(row = 0, column = 1, sticky = E)



def main():
    """ Invokes the program. """
    root = Tk()
    root.title("Movie Recommender")
    app = Application(root)
    root.mainloop()

main()
