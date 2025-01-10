from google_auth_oauthlib.flow import InstalledAppFlow
import os
from dotenv import load_dotenv

load_dotenv()

# TODO: This causes a Google OAuth error at this time.  Need to fix this.
def get_tokens():
    client_config = {
        "web": {
            "client_id": os.getenv("GOOGLE_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
            "redirect_uris": [os.getenv("GOOGLE_REDIRECT_URI")],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }

    flow = InstalledAppFlow.from_client_config(
        client_config,
        scopes=["https://www.googleapis.com/auth/youtube.readonly"]
    )

    credentials = flow.run_local_server(port=8000)

    print("\nAdd these to your .env file:")
    print(f"YT_TOKEN={credentials.token}")
    print(f"YT_REFRESH_TOKEN={credentials.refresh_token}")
    print(f"YT_TOKEN_URI={credentials.token_uri}") # type: ignore
    print(f"YT_CLIENT_ID={credentials.client_id}")
    print(f"YT_CLIENT_SECRET={credentials.client_secret}")
    print(f"YT_SCOPES=https://www.googleapis.com/auth/youtube.readonly")

if __name__ == "__main__":
    get_tokens() 
