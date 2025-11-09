# app/auth.py
import os
from fastapi import Request
from starlette.responses import RedirectResponse
from urllib.parse import urlencode

GOOGLE_OAUTH_CLIENT_ID = os.getenv("GOOGLE_OAUTH_CLIENT_ID")
GOOGLE_OAUTH_CLIENT_SECRET = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET")
GOOGLE_OAUTH_REDIRECT = os.getenv("GOOGLE_OAUTH_REDIRECT", "http://localhost:8000/auth/callback")
SCOPES = ["openid", "email", "profile"]

def google_auth_url(state: str):
    params = {
        "client_id": GOOGLE_OAUTH_CLIENT_ID,
        "redirect_uri": GOOGLE_OAUTH_REDIRECT,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",
        "prompt": "consent",
        "state": state
    }
    return f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"

