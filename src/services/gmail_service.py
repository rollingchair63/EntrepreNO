"""
Gmail service — reads LinkedIn "new connection request" emails
and extracts the person's name for Claude to research.

One-time setup:
    python -m src.services.gmail_service
    (opens browser, saves token.json)
"""

import os
import re
import base64
import logging
from pathlib import Path

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

CREDENTIALS_FILE = Path("credentials.json")
TOKEN_FILE = Path("token.json")


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

def get_gmail_service():
    """Authenticate and return Gmail API service. Opens browser on first run."""
    creds = None

    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                logger.info("Gmail token refreshed.")
            except Exception as e:
                logger.warning(f"Token refresh failed: {e}. Re-authorizing...")
                creds = None

        if not creds:
            if not CREDENTIALS_FILE.exists():
                raise FileNotFoundError(
                    "credentials.json not found.\n"
                    "Download it from Google Cloud Console → Gmail API → OAuth 2.0 Credentials."
                )
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
        logger.info("token.json saved.")

    return build("gmail", "v1", credentials=creds)


# ---------------------------------------------------------------------------
# Fetch LinkedIn connection request emails
# ---------------------------------------------------------------------------

def fetch_connection_requests(max_results: int = 10) -> list[dict]:
    """
    Fetch recent LinkedIn connection request emails.

    Returns list of dicts:
        { name: str, extra_info: str|None, subject: str, email_id: str }
    """
    service = get_gmail_service()

    # LinkedIn sends connection requests from this address
    query = 'from:invitations@linkedin.com (subject:"I want to connect" OR subject:"You have an invitation")'

    results = (
        service.users()
        .messages()
        .list(userId="me", q=query, maxResults=max_results)
        .execute()
    )

    messages = results.get("messages", [])
    if not messages:
        logger.info("No LinkedIn connection request emails found.")
        return []

    requests = []
    for msg_ref in messages:
        try:
            parsed = _parse_connection_email(service, msg_ref["id"])
            if parsed:
                requests.append(parsed)
        except Exception as e:
            logger.warning(f"Failed to parse email {msg_ref['id']}: {e}")

    return requests


def _parse_connection_email(service, msg_id: str) -> dict | None:
    msg = service.users().messages().get(
        userId="me", id=msg_id, format="full"
    ).execute()

    headers = {h["name"]: h["value"] for h in msg["payload"]["headers"]}
    subject = headers.get("Subject", "")
    
    # ✅ Extract name from "From" header 
    from_header = headers.get("From", "")
    name_match = re.match(r'^"?(.+?)"?\s*<', from_header)
    name = name_match.group(1).strip() if name_match else None

    if not name:
        body = _extract_body(msg["payload"])
        name = _extract_name(subject, body)  # fallback

    if not name:
        return None

    body = _extract_body(msg["payload"])
    extra_info = _extract_extra_info(body)

    return {
        "email_id": msg_id,
        "subject": subject,
        "name": name,
        "extra_info": extra_info,
    }


def _extract_body(payload: dict) -> str:
    """Recursively extract plain text from email payload."""
    text = ""
    if payload.get("mimeType") == "text/plain":
        data = payload.get("body", {}).get("data", "")
        if data:
            text += base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
    for part in payload.get("parts", []):
        text += _extract_body(part)
    return text


def _extract_name(subject: str, body: str) -> str | None:
    """Extract person's name from the email subject."""
    patterns = [
        r"^(.+?)\s+wants to connect",
        r"^(.+?)\s+invited you to connect",
        r"^(.+?)\s+has accepted",
        r"^(.+?)\s+accepted your",
    ]
    for pattern in patterns:
        match = re.match(pattern, subject, re.IGNORECASE)
        if match:
            return match.group(1).strip()

    # Fallback: try body
    body_match = re.search(r"([A-Z][a-z]+(?:\s[A-Z][a-z]+)+)\s+wants to connect", body)
    if body_match:
        return body_match.group(1).strip()

    return None


def _extract_extra_info(body: str) -> str | None:
    """
    Try to pull out their headline/title from the email body.
    LinkedIn sometimes includes it under the person's name.
    """
    if not body:
        return None

    lines = [l.strip() for l in body.splitlines() if l.strip()]

    for line in lines:
        if (
            20 <= len(line) <= 120
            and "http" not in line
            and "unsubscribe" not in line.lower()
            and "linkedin.com" not in line.lower()
            and "@" not in line
            and ("|" in line or " at " in line.lower())
        ):
            return line

    return None


# ---------------------------------------------------------------------------
# CLI: run once to authorize
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Authorizing Gmail access...")
    svc = get_gmail_service()
    print("✅ Done! token.json saved.\n")

    print("Fetching latest LinkedIn connection requests...")
    reqs = fetch_connection_requests(max_results=5)

    if reqs:
        for r in reqs:
            print(f"\n📧 {r['subject']}")
            print(f"   Name: {r['name']}")
            if r.get("extra_info"):
                print(f"   Info: {r['extra_info']}")
    else:
        print("No connection request emails found.")