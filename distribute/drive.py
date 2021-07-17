# Google Drive

from pathlib import Path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload
from constants import TOKEN_PATH, CRED_PATH

SCOPES = ["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/spreadsheets"]
FOLDER_ID = "1gPNzISk1AOfJAMiN1KwZ9RCdakwaIgHi"
SHEET_ID = "1DvfcHKmsitkXS9sQ5fuTwesuIwlTq_fzNHQ30NdIlXs"

GREEN_BACKGROUND = {
    "userEnteredFormat": {
        "backgroundColor": {"red": 99 / 255, "green": 210 / 255, "blue": 151 / 255}
    }
}


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
        self.sheets = build("sheets", "v4", credentials=creds).spreadsheets()

    # region Drive

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

    # endregion

    # region Sheets

    def _batch_requests(self, requests):
        if type(requests) == dict:
            requests = [requests]
        r = {"requests": requests}
        return self.sheets.batchUpdate(spreadsheetId=SHEET_ID, body=r).execute()

    # Returns the sums of ranges formatted as cells
    @staticmethod
    def _cells_sums(columns: "list[str]", rows: int):
        return (
            {
                "userEnteredValue": {"formulaValue": f"=SUM({column}2:{column}{rows})"},
                **GREEN_BACKGROUND,
            }
            for column in columns
        )

    def create_sheet(self, title: str) -> int:
        response = self._batch_requests({"addSheet": {"properties": {"title": title, "index": 1}}})
        return response["replies"][0]["addSheet"]["properties"]["sheetId"]

    def upload_to_sheet(self, csv_path: Path, sheet_id: int, rows: int):
        with open(csv_path) as f:
            csv = f.read()
        data_range = {"sheetId": sheet_id, "endColumnIndex": 4, "endRowIndex": rows}
        requests = [
            {  # CSV
                "pasteData": {
                    "coordinate": {"sheetId": sheet_id},
                    "data": csv,
                    "type": "PASTE_NORMAL",
                    "delimiter": ",",
                },
            },
            {  # Alternate colours
                "addBanding": {
                    "bandedRange": {
                        "range": data_range,
                        "rowProperties": {
                            "headerColor": {  # orange/yellow
                                "red": 247 / 255,
                                "green": 203 / 255,
                                "blue": 77 / 255,
                            },
                            "firstBandColor": {  # white
                                "red": 1,
                                "green": 1,
                                "blue": 1,
                            },
                            "secondBandColor": {  # light yellow
                                "red": 254 / 255,
                                "green": 248 / 255,
                                "blue": 227 / 255,
                            },
                        },
                    }
                },
            },
            {  # Change first column width
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": sheet_id,
                        "dimension": "COLUMNS",
                        "startIndex": 0,
                        "endIndex": 1,
                    },
                    "properties": {"pixelSize": 340},
                    "fields": "pixelSize",
                }
            },
            {  # Add totals
                "appendCells": {
                    "sheetId": sheet_id,
                    "rows": [
                        {
                            "values": [
                                {"userEnteredValue": {"stringValue": "Total"}, **GREEN_BACKGROUND},
                                *self._cells_sums(["B", "C", "D"], rows),
                            ]
                        }
                    ],
                    "fields": "userEnteredValue,userEnteredFormat",
                }
            },
            {  # Sort
                "sortRange": {
                    "range": data_range,
                    "sortSpecs": {"sortOrder": "DESCENDING", "dimensionIndex": 2},
                }
            },
        ]
        self._batch_requests(requests)

    def add_blockscout_link(self, sheet_id: int, hash: str):
        link = "https://blockscout.com/xdai/mainnet/tx/" + hash
        req = {
            "updateCells": {
                "start": {"sheetId": sheet_id, "rowIndex": 0, "columnIndex": 5},
                "fields": "userEnteredValue",
                "rows": [{"values": [{"userEnteredValue": {"stringValue": link}}]}],
            }
        }
        self._batch_requests(req)

    # endregion
