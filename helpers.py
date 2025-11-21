import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time
import os

def create_session():
    session = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504]
    )
    session.mount('https://', HTTPAdapter(max_retries=retries))
    return session

def movie_data_from_tmdb(movie_name, count=5):
    try:
        session = create_session()
        url = f"https://api.themoviedb.org/3/search/movie?query={movie_name}&include_adult=false&language=en-US&page=1"
        # Read TMDB Bearer token from environment for security; fall back to embedded token if missing
        bearer = os.environ.get('TMDB_BEARER',
                                'eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJlMjBjMGRlMTU4ZTllYmE1ZjViMDQ1YWFkMmVjYTA3NSIsIm5iZiI6MTcyNDY1Mjk1MC45MzczNDUsInN1YiI6IjVlZTlkYzNlMTY4NWRhMDAzNjI5ODc1ZCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.VQS6z9TVtiem10Ev-1qhecdTEkl0BxpatxEBHoq7KEw')
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {bearer}"
        }
        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        results = response.json()['results']
        if not results:
            return None
        movies_data = []
        for movie in results[:count]:
            movie_id = movie['id']
            url = f"https://api.themoviedb.org/3/movie/{movie_id}?language=en-US"
            resp = session.get(url, headers=headers, timeout=10)
            time.sleep(0.5)  # Add small delay between requests
            resp.raise_for_status()
            movie_data = resp.json()
            poster = f"https://image.tmdb.org/t/p/w500{movie_data['poster_path']}" if movie_data.get('poster_path') else None
            genres = [i['name'] for i in movie_data.get('genres', [])]
            link = movie_data.get('homepage')
            imdb_id = movie_data.get('imdb_id')
            overview = movie_data.get('overview')
            movies_data.append({
                'movie': movie.get('title', movie_name),
                'poster': poster,
                'genres': genres,
                'link': link,
                'imdb_id': imdb_id,
                'overview': overview
            })
        return movies_data
    except Exception as e:
        print(f"Error fetching movie data: {e}")
        return None

if __name__ == '__main__':
    print(movie_data_from_tmdb('inception', count=5))