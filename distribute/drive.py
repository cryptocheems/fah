# Google Drive

from pathlib import Path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload
from constants import TOKEN_PATH, CRED_PATH

SCOPES = ["https://www.googleapis.com/auth/drive"]
FOLDER_ID = "1gPNzISk1AOfJAMiN1KwZ9RCdakwaIgHi"


class Drive:
    def __init__(self) -> None:
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if TOKEN_PATH.exists():
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(CRED_PATH, SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(TOKEN_PATH, "w") as token:
                token.write(creds.to_json())

        self.service = build("drive", "v3", credentials=creds)

    def _upload_file_data(self, metadata, media: MediaFileUpload = None) -> str:
        data = self.service.files().create(body=metadata, fields="id", media_body=media).execute()
        return data.get("id")

    # Returns the id of the folder
    def create_folder(self, name: str) -> str:
        file_metadata = {
            "name": name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [FOLDER_ID],
        }
        return self._upload_file_data(file_metadata)

    def upload_file(self, filename: str, path: Path, folder_id: str):
        media = MediaFileUpload(f"{path}/{filename}")
        file_metadata = {"name": filename, "parents": [folder_id]}
        return self._upload_file_data(file_metadata, media=media)
