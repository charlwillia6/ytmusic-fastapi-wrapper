from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
import os
from dotenv import load_dotenv
from typing import cast

load_dotenv()

def get_tokens() -> None:
    """Get OAuth tokens using local server flow."""
    client_config = {
        "web": {
            "client_id": os.getenv("GOOGLE_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
            "redirect_uris": [os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000")],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }

    flow = InstalledAppFlow.from_client_config(
        client_config,
        scopes=["https://www.googleapis.com/auth/youtube"]
    )

    credentials = cast(Credentials, flow.run_local_server(port=8000))

    print("\nAdd these to your .env file:")
    print(f"YT_TOKEN={credentials.token}")
    print(f"YT_REFRESH_TOKEN={credentials.refresh_token}")
    print(f"YT_TOKEN_URI=https://oauth2.googleapis.com/token")
    print(f"YT_CLIENT_ID={credentials.client_id}")
    print(f"YT_CLIENT_SECRET={credentials.client_secret}")
    print(f"YT_SCOPES=https://www.googleapis.com/auth/youtube")

if __name__ == "__main__":
    get_tokens() 
