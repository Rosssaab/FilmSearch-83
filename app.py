from flask import Flask, render_template, request, jsonify
import requests
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Get the TMDb API key from environment variables
TMDB_API_KEY = os.getenv('TMDB_API_KEY')

logger.debug(f"TMDB_API_KEY loaded: {'Yes' if TMDB_API_KEY else 'No'}")
if TMDB_API_KEY:
    logger.debug(f"TMDB_API_KEY: {TMDB_API_KEY[:5]}...")  # Only log the first 5 characters for security
else:
    logger.error("TMDB_API_KEY is not set in the environment variables")

# TMDb API base URL
TMDB_BASE_URL = "https://api.themoviedb.org/3"

app = Flask(__name__)

def search_person(name):
    endpoint = f"{TMDB_BASE_URL}/search/person"
    params = {
        "api_key": TMDB_API_KEY,
        "query": name,
        "language": "en-US",
        "page": 1
    }
    try:
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        data = response.json()
        if data['results']:
            return data['results'][0]['id']  # Return the ID of the first person found
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error searching for person: {e}")
        raise

def search_movies(title, year=None, person=None):
    endpoint = f"{TMDB_BASE_URL}/search/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "language": "en-US",
        "page": 1,
        "include_adult": "false"
    }

    if title:
        params["query"] = title
    if year:
        params["year"] = year

    try:
        if person:
            person_id = search_person(person)
            if person_id:
                # If searching by person, use the discover endpoint instead
                endpoint = f"{TMDB_BASE_URL}/discover/movie"
                params["with_cast"] = person_id
                params["sort_by"] = "popularity.desc"
            else:
                logger.debug(f"No person found for: {person}")

        logger.debug(f"Sending request to TMDb API with params: {params}")
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        data = response.json()
        logger.debug(f"Received response from TMDb API: {data}")
        return data
    except requests.exceptions.RequestException as e:
        logger.error(f"Error searching for movies: {e}")
        raise

def get_movie_videos(movie_id):
    endpoint = f"{TMDB_BASE_URL}/movie/{movie_id}/videos"
    params = {
        "api_key": TMDB_API_KEY,
        "language": "en-US"
    }
    try:
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        data = response.json()
        # Filter for YouTube trailers
        trailers = [video for video in data.get('results', []) if video['site'] == 'YouTube' and video['type'] == 'Trailer']
        return trailers[0]['key'] if trailers else None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching movie videos: {e}")
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    movies = []
    error = None
    theme = request.args.get('theme', 'cyborg')
    total_pages = 0

    if request.method == 'POST':
        try:
            title = request.form.get('title', '').strip()
            year = request.form.get('year', '').strip()
            person = request.form.get('person', '').strip()

            if not (title or year or person):
                error = "Please enter at least one search criteria."
            else:
                logger.debug(f"Searching for movies with title: {title}, year: {year}, person: {person}")

                data = search_movies(title=title, year=year, person=person)

                if 'results' in data and data['results']:
                    movies = data['results']
                    total_pages = data.get('total_pages', 0)
                    logger.debug(f"Found {len(movies)} movies, total pages: {total_pages}")
                    for movie in movies:
                        movie['trailer_key'] = get_movie_videos(movie['id'])
                else:
                    error = "No movies found matching your criteria."
                    logger.debug("No movies found in the API response")

        except Exception as e:
            logger.exception(f"An error occurred during search: {str(e)}")
            error = f"An error occurred: {str(e)}"

    return render_template('index.html', movies=movies, error=error, theme=theme, total_pages=total_pages)

@app.route('/load_more', methods=['POST'])
def load_more():
    page = int(request.form.get('page', 1))
    title = request.form.get('title', '')
    year = request.form.get('year', '')
    person = request.form.get('person', '')

    data = search_movies(title=title, year=year, person=person, page=page)

    if 'results' in data and data['results']:
        movies = data['results']
        for movie in movies:
            movie['trailer_key'] = get_movie_videos(movie['id'])
        return jsonify({
            'movies': movies,
            'total_pages': data.get('total_pages', 0)
        })
    else:
        return jsonify({'error': 'No more movies found'}), 404

@app.route('/<theme>')
def themed_index(theme):
    return index()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8083)
