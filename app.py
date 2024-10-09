from flask import Flask, render_template, request
import requests
import os
from dotenv import load_dotenv
from waitress import serve
import base64
import logging
import time

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Get the Spotify API credentials from environment variables
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')

# Add this debug logging to verify the credentials are loaded correctly
print(f"SPOTIFY_CLIENT_ID: {SPOTIFY_CLIENT_ID}")
print(f"SPOTIFY_CLIENT_SECRET: {SPOTIFY_CLIENT_SECRET[:5]}...") # Only print the first 5 characters for security

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug(f"SPOTIFY_CLIENT_ID: {SPOTIFY_CLIENT_ID}")
logger.debug(f"SPOTIFY_CLIENT_SECRET: {SPOTIFY_CLIENT_SECRET[:5]}...") # Only log the first 5 characters for security

# Global variables for token management
spotify_token = None
token_expiration_time = 0

def get_spotify_token():
    global spotify_token, token_expiration_time
    
    if spotify_token and time.time() < token_expiration_time:
        return spotify_token

    auth_string = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": f"Basic {auth_base64}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    
    try:
        response = requests.post(url, headers=headers, data=data)
        logger.debug(f"Token request status code: {response.status_code}")
        logger.debug(f"Token request response: {response.text}")
        response.raise_for_status()
        json_result = response.json()
        
        if 'access_token' not in json_result:
            logger.error(f"Access token not found in response. Response: {json_result}")
            raise ValueError("Access token not found in Spotify API response")
        
        spotify_token = json_result["access_token"]
        token_expiration_time = time.time() + json_result.get("expires_in", 3600)
        return spotify_token
    except requests.exceptions.RequestException as e:
        logger.error(f"Error obtaining Spotify access token: {e}")
        logger.error(f"Response content: {e.response.text if e.response else 'No response content'}")
        raise

@app.route('/', methods=['GET', 'POST'])
def index():
    songs = []
    error = None
    theme = request.args.get('theme', 'quartz')  # Default theme is quartz

    if request.method == 'POST':
        try:
            # Get search parameters
            track = request.form.get('track', '')
            artist = request.form.get('artist', '')
            album = request.form.get('album', '')

            # Construct the query
            query = '+'.join(filter(None, [
                f'track:{track}' if track else '',
                f'artist:{artist}' if artist else '',
                f'album:{album}' if album else ''
            ]))

            # Get Spotify access token
            token = get_spotify_token()

            # Make a request to the Spotify API
            url = f'https://api.spotify.com/v1/search?q={query}&type=track'
            headers = {
                "Authorization": f"Bearer {token}"
            }
            response = requests.get(url, headers=headers)
            logger.debug(f"Search request status code: {response.status_code}")
            logger.debug(f"Search request response: {response.text[:200]}...")  # Log first 200 characters
            response.raise_for_status()
            data = response.json()

            # Check if there are any songs returned
            if 'tracks' in data and 'items' in data['tracks']:
                songs = data['tracks']['items']
            else:
                error = "No songs found matching your criteria."

        except Exception as e:
            logger.exception(f"An error occurred during search: {str(e)}")
            error = f"An error occurred: {str(e)}"

    return render_template('index.html', songs=songs, error=error, theme=theme)

@app.route('/<theme>')
def themed_index(theme):
    return index()

if __name__ == '__main__':
    from waitress import serve
    print("Starting server on http://localhost:8080")
    serve(app, host='127.0.0.1', port=8080)