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
|   |   ├── logger.py
|   |   ├── middleware.py
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
│   │   ├── test_explore.py
│   │   ├── test_library.py
│   │   ├── test_playlists.py
│   │   ├── test_podcasts.py
│   │   ├── test_search.py
│   │   ├── test_security.py
│   │   ├── test_uploads.py
│   │   └── test_watcg.py
│   ├── test_services/
│   │   └── test_ytmusic.py
│   └── conftest.py
├── logs/
│   ├── app.log
│   └── security.log
├── scripts/
|   ├── reacreate_db.py
│   └── get_tokens.py
├── .env.example
├── .gitignore
├── API_USAGE.md
├── client_secrets.json.example
├── Dockerfile
├── LICENSE
├── pytest.ini
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
- Docker (optional, for containerized deployment)
- Git

## Environment Variables

### Required

- `GOOGLE_CLIENT_ID`: Your Google OAuth2 client ID
- `GOOGLE_CLIENT_SECRET`: Your Google OAuth2 client secret
- `GOOGLE_REDIRECT_URI`: OAuth2 callback URL (e.g., <http://localhost:8000/api/v1/auth/callback>)
- `GOOGLE_REDIRECT_URI_DOCS`: OAuth2 Swagger docs redirect URL (e.g., <http://localhost:8000/api/v1/docs/oauth2-redirect>)

### Optional

- `DATABASE_URL`: Database connection string (default: sqlite:///./app.db)
- `DEBUG`: Enable debug mode (default: false)
- `RATE_LIMIT_MAX_REQUESTS`: Max requests per window (default: 50)
- `RATE_LIMIT_WINDOW`: Time window in seconds (default: 60)
- `BRUTE_FORCE_MAX_ATTEMPTS`: Max login attempts (default: 5)
- `BRUTE_FORCE_WINDOW`: Brute force window in seconds (default: 300)

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

2. Visit `http://localhost:8000/api/v1/docs` for the interactive API documentation.

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

## Security

- Rate limiting (50 requests per minute per IP)
- Brute force protection (5 attempts per 5 minutes)
- Required User-Agent headers
- OAuth2 token validation
- HTTPS redirect in production

## Docker Deployment

Build and run the application using Docker:

```bash
# Build the image
docker build -t ytmusic-api .

# Run the container
docker run -p 8000:8000 \
-e GOOGLE_CLIENT_ID=your_client_id \
-e GOOGLE_CLIENT_SECRET=your_client_secret \
-e GOOGLE_REDIRECT_URI=your_redirect_uri \
-e GOOGLE_REDIRECT_URI_DOCS=your_docs_redirect_uri \
-e DATABASE_URL=sqlite:///./app.db \
-e DEBUG=False \
# Optional rate limiting and security
-e RATE_LIMIT_MAX_REQUESTS=50 \
-e RATE_LIMIT_WINDOW=60 \
-e BRUTE_FORCE_MAX_ATTEMPTS=5 \
-e BRUTE_FORCE_WINDOW=300 \
ytmusic-api
```

## API Documentation

Please see [API_USAGE.md](API_USAGE.md) for detailed API documentation, or visit the interactive API documentation at:

- Swagger UI: `http://localhost:8000/api/v1/docs`
- ReDoc: `http://localhost:8000/api/v1/redoc`

The interactive documentation provides a complete reference of all endpoints, request/response schemas, and allows testing the API directly from your browser.

## Troubleshooting

### Common issues and solutions

1. OAuth2 Authentication Errors
   - Verify your Google OAuth2 credentials
   - Ensure redirect URI matches exactly
   - Check scope permissions
2. Rate Limiting
   - Default limit is 50 requests per minute
   - Increase limits via environment variables if needed
3. Database Issues
   - Run `python scripts/recreate_db.py` to reset the database
   - Check database connection string in .env

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
