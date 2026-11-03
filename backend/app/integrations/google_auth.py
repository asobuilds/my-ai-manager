"""Google OAuth2 authentication helper."""
from __future__ import annotations

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/calendar.readonly",
]


def get_flow(client_id: str, client_secret: str, redirect_uri: str) -> Flow:
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=SCOPES,
        redirect_uri=redirect_uri,
    )
    return flow


def generate_authorization_url(
    client_id: str, client_secret: str, redirect_uri: str, state: str = ""
) -> str:
    flow = get_flow(client_id, client_secret, redirect_uri)
    authorization_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        state=state,
        prompt="consent",
    )
    return authorization_url


def exchange_authorization_code(
    client_id: str, client_secret: str, redirect_uri: str, code: str
) -> tuple[str, str | None, int]:
    flow = get_flow(client_id, client_secret, redirect_uri)
    flow.fetch_token(authorization_response=f"https://localhost?code={code}")
    credentials = Credentials(flow.token_uri, flow.client_id, flow.client_secret,
                              flow.refresh_token, flow.token, flow.token_uri,
                              flow.token_backend)
    return credentials.token, credentials.refresh_token, credentials.token_expiry.timestamp()
