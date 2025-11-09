# app/storage.py
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# This module assumes a SERVICE ACCOUNT JSON credential in env or file.
# Alternatively, implement OAuth user flow to upload into user's Drive.
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")  # path to json file
DRIVE_FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID")

def get_drive_service():
    if not SERVICE_ACCOUNT_FILE:
        raise RuntimeError("Set GOOGLE_SERVICE_ACCOUNT_JSON env var to path of service account json")
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=["https://www.googleapis.com/auth/drive"])
    service = build("drive", "v3", credentials=creds, cache_discovery=False)
    return service

def upload_file_to_drive(local_path: str, name: str, mimetype: str = None) -> str:
    service = get_drive_service()
    file_metadata = {"name": name}
    if DRIVE_FOLDER_ID:
        file_metadata["parents"] = [DRIVE_FOLDER_ID]
    media = MediaFileUpload(local_path, mimetype=mimetype, resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields="id, webViewLink").execute()
    link = file.get("webViewLink")
    return link

