# YTMusic FastAPI Wrapper

A FastAPI-based wrapper for the YouTube Music API that provides a RESTful interface for interacting with YouTube Music.

## Project Structure

```
ytmusic-fastapi-wrapper/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── auth.py
│   │       │   ├── browse.py
│   │       │   ├── explore.py
│   │       │   ├── library.py
│   │       │   ├── playlists.py
│   │       │   ├── podcasts.py
│   │       │   ├── search.py
│   │       │   ├── uploads.py
│   │       │   └── watch.py
│   │       └── router.py
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   ├── db/
│   │   ├── models.py
│   │   └── session.py
│   ├── schemas/
│   │   └── models.py
│   ├── services/
│   │   └── ytmusic.py
│   └── main.py
├── tests/
│   ├── test_api/
│   │   ├── test_auth.py
│   │   ├── test_browse.py
│   │   ├── test_library.py
│   │   ├── test_playlists.py
│   │   └── test_search.py
│   ├── test_services/
│   │   └── test_ytmusic.py
│   └── conftest.py
├── .env
├── .gitignore
├── Dockerfile
├── README.md
└── requirements.txt
```

## Features

- OAuth2 authentication with YouTube API
- Playlist management (create, edit, delete)
- Search functionality
- Library management
- Browse functionality
- Upload management

## Prerequisites

- Python 3.8+
- pip
- Google OAuth2 credentials

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/ytmusic-fastapi-wrapper.git
   cd ytmusic-fastapi-wrapper
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   .\venv\Scripts\activate  # Windows
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your OAuth2 credentials:

   ```env
   GOOGLE_CLIENT_ID=your_client_id
   GOOGLE_CLIENT_SECRET=your_client_secret
   GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/callback
   DATABASE_URL=sqlite:///./app.db  # SQLite database URL (default)
   DEBUG=false  # Set to true for debug mode
   ```

5. Get your YouTube tokens:

   ```bash
   python scripts/get_tokens.py
   ```

   Follow the prompts and add the generated YT_* variables to your .env file.

## Running the Application

1. Start the server:

   ```bash
   uvicorn app.main:app --reload
   ```

2. Visit `http://localhost:8000/docs` for the interactive API documentation.

## Testing

The project includes a comprehensive test suite that covers API endpoints and services. Tests are organized to mirror the application structure:

- `tests/test_api/`: Tests for API endpoints
- `tests/test_services/`: Tests for service layer
- `tests/conftest.py`: Shared test fixtures and configuration

To run the tests:

```bash
# Run all tests
pytest

# Run tests with coverage report
pytest --cov=app

# Run specific test file
pytest tests/test_api/test_auth.py

# Run tests with verbose output
pytest -v
```

The test suite uses pytest fixtures for:

- FastAPI test client
- Authentication headers
- Mock YTMusic service

Tests are written using pytest and include:

- Unit tests for all endpoints
- Authentication flow testing
- Service layer mocking
- Error handling verification

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [ytmusicapi](https://github.com/sigma67/ytmusicapi) for the YouTube Music API implementation
- [FastAPI](https://fastapi.tiangolo.com/) for the web framework

This project is built upon the excellent [ytmusicapi](https://github.com/sigma67/ytmusicapi) library. We extend our sincere gratitude to the
ytmusicapi developers and contributors for creating and maintaining such a robust foundation that makes this wrapper possible. The ytmusicapi
library provides the core functionality for interacting with YouTube's internal APIs, which this project leverages to provide a REST API
interface. For more information about the underlying library, please visit the [ytmusicapi documentation](https://ytmusicapi.readthedocs.io/).

## Disclaimer

This project is an independent, unofficial implementation and is not affiliated with, endorsed by, or in any way officially connected to
YouTube, YouTube Music, or Google LLC. The ytmusicapi library that this project depends on provides unofficial access to YouTube's internal
APIs. While we strive to maintain compatibility, please be aware that as an unofficial API, functionality may change without notice if YouTube
Music modifies their internal systems. Use of this software is at your own discretion and risk.
