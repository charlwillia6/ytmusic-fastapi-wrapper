import os
from dotenv import load_dotenv
from typing import List, Optional

load_dotenv()

# Required OAuth variables
GOOGLE_CLIENT_ID: Optional[str] = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET: Optional[str] = os.environ.get("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI: Optional[str] = os.environ.get("GOOGLE_REDIRECT_URI")
GOOGLE_REDIRECT_URI_DOCS: Optional[str] = os.environ.get("GOOGLE_REDIRECT_URI_DOCS")

# Optional security variables with defaults
RATE_LIMIT_MAX_REQUESTS: int = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "50"))
RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))
BRUTE_FORCE_MAX_ATTEMPTS: int = int(os.getenv("BRUTE_FORCE_MAX_ATTEMPTS", "5"))
BRUTE_FORCE_WINDOW: int = int(os.getenv("BRUTE_FORCE_WINDOW", "300"))

# Debug prints
DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
if DEBUG:
    print("Environment variables loaded:")
    print(f"GOOGLE_CLIENT_ID: {GOOGLE_CLIENT_ID[:10]}..." if GOOGLE_CLIENT_ID else "Not set")
    print(f"GOOGLE_CLIENT_SECRET: {GOOGLE_CLIENT_SECRET[:5]}..." if GOOGLE_CLIENT_SECRET else "Not set")
    print(f"GOOGLE_REDIRECT_URI: {GOOGLE_REDIRECT_URI}" if GOOGLE_REDIRECT_URI else "Not set")
    print(f"GOOGLE_REDIRECT_URI_DOCS: {GOOGLE_REDIRECT_URI_DOCS}" if GOOGLE_REDIRECT_URI_DOCS else "Not set")
    print(f"Rate Limit: {RATE_LIMIT_MAX_REQUESTS} requests per {RATE_LIMIT_WINDOW} seconds")
    print(f"Brute Force Protection: {BRUTE_FORCE_MAX_ATTEMPTS} attempts per {BRUTE_FORCE_WINDOW} seconds")

# Environment variable validation
required_vars = [
    "GOOGLE_CLIENT_ID",
    "GOOGLE_CLIENT_SECRET",
    "GOOGLE_REDIRECT_URI",
    "GOOGLE_REDIRECT_URI_DOCS",
]

for var in required_vars:
    if not os.getenv(var):
        raise ValueError(f"Missing required environment variable: {var}")

# OAuth scopes
SCOPES: List[str] = [
    'https://www.googleapis.com/auth/youtube',
    'https://www.googleapis.com/auth/youtube.readonly'
] 
