# TMDB Film Search

This is a Flask-based web application that allows users to search for films using The Movie Database (TMDB) API.

## Features

- Search films by title, year, and person (actor/director)
- Display film details including poster, release date, and overview
- Watch film trailers (when available)
- Responsive design with customizable themes
- Load more results functionality

## Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up your TMDB API key in a `.env` file:
   ```
   TMDB_API_KEY=your_api_key_here
   ```
4. Run the app: `python app.py`

## Technologies Used

- Flask
- TMDB API
- Bootstrap
- JavaScript

## Usage

1. Enter a film title, release year, or person's name (actor/director) in the search fields.
2. Click the "Search" button to find matching films.
3. Browse through the results, read film descriptions, and watch trailers if available.
4. Use the "Load More" button to see additional results.
5. Click "Search Again" to start a new search.

## Customization

You can change the visual theme of the application using the dropdown menu in the navigation bar.

## Contributing

Contributions to improve the application are welcome. Please feel free to submit a Pull Request.

## License

[MIT License](LICENSE)

## Acknowledgements

- This project uses the TMDB API but is not endorsed or certified by TMDB.
- Thanks to the Flask and Bootstrap communities for their excellent documentation and resources.