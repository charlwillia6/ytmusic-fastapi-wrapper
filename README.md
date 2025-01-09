# ytmusic-playlist-studio-backend

This project is a backend REST API built with FastAPI that wraps the ytmusicapi library. It provides endpoints for managing YouTube Music playlists and accessing the user's music library. It also handles authentication via Google OAuth 2.0 and manages user sessions using a SQLite database.

## Development Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/charlwillia6/ytmusic-playlist-creator-backend.git
   cd ytmusic-playlist-creator-backend
   ```

2. Navigate to the project directory: `cd ytmusic-playlist-backend`
3. Create a virtual environment: `python -m venv venv`
4. Activate the virtual environment:

   ```bash
   # On Windows:
    .\venv\Scripts\activate
    # On Unix or MacOS:
    source venv/bin/activate
    ```

5. Install the dependencies: `pip install -r requirements.txt`
6. Set up environment variables:

   - Create a .env file in the project root with the following:

        ```bash
        GOOGLE_CLIENT_ID=your_client_id
        GOOGLE_CLIENT_SECRET=your_client_secret
        GOOGLE_REDIRECT_URI=http://localhost:8000/auth/callback
        DATABASE_URL=sqlite:///./sessions.db
        ```

        Note: You'll need to:

        - Create a project in the Google Cloud Console
        - Enable the YouTube Data API v3
        - Create OAuth 2.0 credentials
        - Add <http://localhost:8000/auth/callback> to the authorized redirect URIs

7. Run the application: `uvicorn main:app --reload --port 8000`
8. Access the application:
   - API: <http://localhost:8000>
   - Interactive API documentation: <http://localhost:8000/doc>
   - Alternative API documentation: <http://localhost:8000/redoc>

### Development Tools

- API Documentation: FastAPI automatically generates interactive API documentation at /docs and /redoc
- Hot Reload: The --reload flag enables automatic reloading when code changes are detected
- Database: SQLite database file will be created automatically in your project directory
- Debug Mode: Add --debug flag to uvicorn command for detailed logs

## API Documentation

For detailed API endpoint documentation and usage examples, please see [USAGE.md](USAGE.md).

## Deployment

To deploy the application to Google Cloud Run, you will need to:

1. Install and configure the Google Cloud SDK (`gcloud`).
2. Build the Docker image: `docker build -t ytmusic-playlist-backend .`
3. Tag the image for Google Container Registry: `docker tag ytmusic-playlist-backend gcr.io/[your-project-id]/ytmusic-playlist-backend`
4. Push the image to Google Container Registry: `docker push gcr.io/[your-project-id]/ytmusic-playlist-backend`
5. Deploy the image to Google Cloud Run: `gcloud run deploy ytmusic-playlist-backend --image gcr.io/[your-project-id]/ytmusic-playlist-backend --platform managed --allow-unauthenticated --port 8080`

Replace `[your-project-id]` with your actual Google Cloud project ID.

## Testing

This section provides detailed instructions on how to run and understand the test suite for the YTMusic Playlist Creator Backend.

### Test Structure

The test suite consists of two main test files:

- `test_main.py`: Tests the FastAPI endpoints and application logic
- `test_ytmusic.py`: Tests the YTMusic integration functionality separately

### Prerequisites

Before running the tests, ensure you have the following installed:

1. Python 3.8 or higher
2. Virtual environment (recommended)
3. Required packages:

```bash
pip install pytest pytest-mock pytest-asyncio httpx fastapi sqlalchemy ytmusicapi python-dotenv
```

### Setting Up the Test Environment

1. Create a `.env` file for testing:

```env
GOOGLE_CLIENT_ID=your_test_client_id
GOOGLE_CLIENT_SECRET=your_test_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/callback

# For integration tests (optional)
YT_TOKEN=your_youtube_token
YT_REFRESH_TOKEN=your_refresh_token
YT_TOKEN_URI=your_token_uri
YT_CLIENT_ID=your_client_id
YT_CLIENT_SECRET=your_client_secret
YT_SCOPES=https://www.googleapis.com/auth/youtube.readonly
```

### Running the Tests

#### Running FastAPI Tests (test_main.py)

These tests cover the API endpoints and application logic:

```bash
# Run all FastAPI tests
pytest test_main.py -v

# Run specific test
pytest test_main.py -v -k "test_create_playlist"

# Run with coverage report
pytest test_main.py -v --cov=app --cov-report=term-missing
```

#### Running YTMusic Integration Tests (test_ytmusic.py)

These tests cover the YTMusic client functionality:

```bash
# Run all YTMusic tests except integration tests
pytest test_ytmusic.py -v

# Run including integration tests (requires real credentials)
pytest test_ytmusic.py -v --runintegration

# Run specific test
pytest test_ytmusic.py -v -k "test_playlist_creation"
```

### Test Categories

#### FastAPI Tests (test_main.py)

- Authentication tests
- Playlist management tests
- Search functionality tests
- Library management tests
- User session tests

#### YTMusic Tests (test_ytmusic.py)

- Playlist operations
- Search functionality
- Library management
- Artist information
- Song rating
- Watch playlist functionality
- Integration tests with real API (optional)

### Understanding Test Output

The test output will show:

- Number of tests run
- Number of tests passed/failed
- Test execution time
- Detailed error messages for failed tests

Example output:

```bash
============================= test session starts ==============================
platform win32 -- Python 3.8.0, pytest-6.2.4, py-1.10.0, pluggy-0.13.1
rootdir: C:\path\to\project
plugins: hypothesis-6.75.3, cov-4.1.0, asyncio-0.12.0
collected 20 items

test_main.py::test_auth_login PASSED                                    [  5%]
test_main.py::test_auth_callback PASSED                                [ 10%]
...
```

### Writing New Tests

When adding new tests:

1. For API endpoints (test_main.py):

    ```python
    @patch("main.YTMusic.your_method")
    def test_your_endpoint(mock_method, client, test_db):
        # Arrange
        mock_method.return_value = your_expected_return
        
        # Create test session
        session_token = create_test_session(test_db)
        
        # Act
        response = client.get("/your-endpoint", headers={"session_token": session_token})
        
        # Assert
        assert response.status_code == 200
        assert response.json() == expected_response
    ```

2. For YTMusic functionality (test_ytmusic.py):

    ```python
    def test_your_ytmusic_function(self, ytmusic_client):
        # Arrange
        expected_result = {"your": "test_data"}
        ytmusic_client.your_method.return_value = expected_result
        
        # Act
        result = ytmusic_client.your_method()
        
        # Assert
        assert result == expected_result
        ytmusic_client.your_method.assert_called_once()
    ```

### Troubleshooting

Common issues and solutions:

1. **Missing Dependencies**

    ```bash
    pip install -r requirements.txt
    ```

2. **Database Errors**
   - Ensure SQLite is available
   - Check database permissions
   - Verify test database configuration

3. **Integration Test Failures**
   - Verify environment variables are set correctly
   - Check API credentials are valid
   - Ensure network connectivity

4. **Test Discovery Issues**
   - Ensure test files are named correctly (test_*.py)
   - Verify test functions are named correctly (test_*)
   - Check pytest configuration

### Contributing Tests

When contributing new tests:

1. Follow the existing test structure and naming conventions
2. Include both positive and negative test cases
3. Mock external dependencies appropriately
4. Add documentation for new test cases
5. Ensure all tests pass before submitting PR

### Additional Testing Resources

- [pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing Documentation](https://fastapi.tiangolo.com/tutorial/testing/)
- [YTMusic API Documentation](https://ytmusicapi.readthedocs.io/)
