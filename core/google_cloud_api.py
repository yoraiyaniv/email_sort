import os
from typing import List
import base64

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request


# Scopes: read-only access is enough to list labels
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly", "https://www.googleapis.com/auth/gmail.modify"]

def get_gmail_service() -> "googleapiclient.discovery.Resource":
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists("credentials.json"):
                raise FileNotFoundError("Missing credentials.json")
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as f:
            f.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)

def get_user_labels(service) -> dict:
    """Return only user-created label names."""
    labels = service.users().labels().list(userId="me").execute().get("labels", [])
    return {lbl["name"]: lbl["id"] for lbl in labels if lbl.get("type") == "user"}

def label_email(service, msg_id: str, label_id: str):
    """Apply a label to an email."""
    if label_id:
        service.users().messages().modify(
            userId="me",
            id=msg_id,
            body={"addLabelIds": [label_id]}
        ).execute()
    else:
        raise ValueError("Label ID is None or empty.")

def get_messages_in_time_window(service, start_time: str, end_time: str) -> List[str]:
    """Fetch message IDs within a specific time window."""
    query = f"after:{start_time} before:{end_time} is:unread"
    response = service.users().messages().list(userId="me", q=query).execute()
    messages = response.get("messages", [])
    return [msg["id"] for msg in messages]

def get_email_content(service, msg_id: str) -> str:
    """Fetch the full email content given a message ID."""
    message = service.users().messages().get(userId="me", id=msg_id, format="full").execute()
    parts = message.get("payload", {}).get("parts", [])
    for part in parts:
        if part.get("mimeType") == "text/plain":
            data = part.get("body", {}).get("data", "")
            return base64.urlsafe_b64decode(data).decode("utf-8")
    return ""  # Fallback if no text/plain part is found

def mark_email_as_read(service, msg_id: str):
    """Mark an email as read."""
    service.users().messages().modify(
        userId="me",
        id=msg_id,
        body={"removeLabelIds": ["UNREAD"]}
    ).execute()