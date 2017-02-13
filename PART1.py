import requests
import sqlite3

conn = sqlite3.connect('watchedlist.db')
cur = conn.cursor()

# genre dictionary
genredict = {'Action':0, 'Adventure':0, 'Animation':0, 'Biography':0, 'Comedy':0,
             'Crime':0, 'Documentary':0, 'Drama':0, 'Family':0, 'Fantasy':0,
             'Film-Noir':0, 'Game-Show':0, 'History':0, 'Horror':0, 'Music':0,
             'Musical':0, 'Mystery':0, 'News':0, 'Reality-TV':0, 'Romance':0,
             'Sci-Fi':0, 'Sport':0, 'Talk-Show':0, 'Thriller':0, 'War':0, 'Western':0}
directordict = dict()
filmcount = 0

# converts watched list id to imdb_id
def idConverter(id):
    new_id = "tt" + (7-len(id)) * "0" + id
    return new_id

cur.execute('SELECT * FROM movie_watched')
result = cur.fetchall()

for row in result:
    id = str(row[0])
    new_id = idConverter(id)

    url = "http://www.omdbapi.com/?i=" + new_id + "&plot=short&r=json"
    print(url)

    uh = requests.get(url)
    info = uh.json()
    
    title = info['Title']
    genre = info['Genre']
    director = info['Director']
    rating = info['imdbRating']
    year = info['Year']
    imdb_id = int(id)

    print(title, genre, director, rating)

    genres = genre.split(',')
    for genre in genres:
        genre = genre.strip()
        genredict[genre] = genredict.get(genre) + 1
        
    filmcount = filmcount + 1

    conn.commit()

cur

# weighting for each Genre
wdict1 = {'Action':1, 'Adventure':1, 'Animation':2, 'Biography':2, 'Comedy':0.8,
        'Crime':1, 'Documentary':5, 'Drama':0.5, 'Family':2, 'Fantasy':2,
        'Film-Noir':4, 'Game-Show':1, 'History':3, 'Horror':3, 'Music':4,
        'Musical':4, 'Mystery':2, 'News':1, 'Reality-TV':1, 'Romance':1.5,
        'Sci-Fi':2, 'Sport':4, 'Talk-Show':1, 'Thriller':1.1, 'War':2.5, 'Western':4}

wdict2 = wdict1.copy()
for k,v in wdict2.items():
    wdict2[k] = v * genredict[k]

print(wdict2)


# algorithm
conn2 = sqlite3.connect('booleantopmovies.db')
cur2 = conn2.cursor()

cur2.execute('SELECT * FROM GenresB')
allmovies = cur2.fetchall()


watched_movies = cur.execute('SELECT imdb_id FROM Movies')

scores = []
for row in allmovies:
    if row[0] in watched_movies: continue
    c = 0
    score = (wdict2['Action'] * row[2] +
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
    scores.append( (row[1], score) )

ordered = sorted(scores, key=lambda movie: movie[1], reverse = True)
top5 = ordered[:5]
for movie in top5:
    print(movie[0], movie[1])
                 
