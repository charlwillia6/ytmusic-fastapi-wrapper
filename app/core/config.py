import os
from dotenv import load_dotenv
from typing import List, Optional

load_dotenv()

GOOGLE_CLIENT_ID: Optional[str] = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET: Optional[str] = os.environ.get("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI: Optional[str] = os.environ.get("GOOGLE_REDIRECT_URI")

# Debug prints
DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
if DEBUG:
    print("Environment variables loaded:")
    print(f"GOOGLE_CLIENT_ID: {GOOGLE_CLIENT_ID[:10]}..." if GOOGLE_CLIENT_ID else "Not set")
    print(f"GOOGLE_CLIENT_SECRET: {GOOGLE_CLIENT_SECRET[:5]}..." if GOOGLE_CLIENT_SECRET else "Not set")
    print(f"GOOGLE_REDIRECT_URI: {GOOGLE_REDIRECT_URI}" if GOOGLE_REDIRECT_URI else "Not set")

# Environment variable validation
required_vars = [
    "GOOGLE_CLIENT_ID",
    "GOOGLE_CLIENT_SECRET",
    "GOOGLE_REDIRECT_URI",
]

for var in required_vars:
    if not os.getenv(var):
        raise ValueError(f"Missing required environment variable: {var}")

# OAuth scopes
SCOPES: List[str] = [
    'https://www.googleapis.com/auth/youtube.readonly'
] 
