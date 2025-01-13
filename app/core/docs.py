from fastapi import FastAPI
from fastapi.openapi.models import OAuthFlows, OAuthFlowImplicit

def configure_swagger_oauth(app: FastAPI):
    """Configure Swagger UI OAuth settings"""
    app.swagger_ui_init_oauth = {
        "clientId": "YOUR_GOOGLE_CLIENT_ID",
        "appName": "YTMusic API",
        "usePkceWithAuthorizationCodeGrant": True,
        "scopes": "https://www.googleapis.com/auth/youtube"
    }

    # Update OpenAPI schema security definitions
    if app.openapi_schema:
        app.openapi_schema["components"]["securitySchemes"] = {
            "google_oauth2": {
                "type": "oauth2",
                "flows": {
                    "authorizationCode": {
                        "authorizationUrl": "https://accounts.google.com/o/oauth2/v2/auth",
                        "tokenUrl": "https://oauth2.googleapis.com/token",
                        "scopes": {
                            "https://www.googleapis.com/auth/youtube": "Access YouTube data",
                            "https://www.googleapis.com/auth/youtube.readonly": "Read-only access"
                        }
                    }
                }
            }
        } 
