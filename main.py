import pandas as pd

# read CSVs
movies = pd.read_csv('datas/movies.csv')
ratings = pd.read_csv('datas/ratings.csv')

# merge on movieId column
data = pd.merge(left=movies, right=ratings, on='movieId')


years = []

for title in data['title']:
    year_subset = title[-5:-1]
    try: years.append(int(year_subset))
    except: years.append(9999)
        
data['moviePubYear'] = years
print(len(data[data['moviePubYear'] == 9999]))


genre_df = pd.DataFrame(data['genres'].str.split('|').tolist(), index=data['movieId']).stack()
genre_df = genre_df.reset_index([0, 'movieId'])
genre_df.columns = ['movieId', 'Genre']
genre_df.head()

num_ratings = pd.DataFrame(data.groupby('movieId').count()['rating']).reset_index()
data = pd.merge(left=data, right=num_ratings, on='movieId')
data.rename(columns={'rating_x': 'rating', 'rating_y': 'numRatings'}, inplace=True)

data.sort_values(by='numRatings', ascending=False).drop_duplicates('movieId')[:10]
matrix = data.pivot_table(
    index='userId',
    columns='title',
    values='rating'
)

def get_similar_movies(movie_title, n_ratings_filter=100, n_recommendations=5):
    similar = matrix.corrwith(matrix[movie_title])
    corr_similar = pd.DataFrame(similar, columns=['correlation'])
    corr_similar.dropna(inplace=True)
    
    orig = data.copy()
    
    corr_with_movie = pd.merge(
        left=corr_similar, 
        right=orig, 
        on='title')[['title', 'correlation', 'numRatings']].drop_duplicates().reset_index(drop=True)
    
    result = corr_with_movie[corr_with_movie['numRatings'] > n_ratings_filter].sort_values(by='correlation', ascending=False)
    
    return result.head(n_recommendations)

get_similar_movies('Pulp Fiction (1994)')