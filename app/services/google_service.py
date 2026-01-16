import os
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import logging

logger = logging.getLogger(__name__)

# Scopes required for the application
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',  # Read and write spreadsheets
    'https://www.googleapis.com/auth/drive',  # Access to Drive files
    'https://www.googleapis.com/auth/forms.body',  # Create and edit forms
    'https://www.googleapis.com/auth/forms.responses.readonly'  # Read form responses
]

class GoogleService:
    def __init__(self, credentials_path='credentials.json', token_path='token.pickle'):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.creds = None
        self.sheets_service = None
        self.drive_service = None

    def authenticate(self):
        """Authenticate with Google APIs"""
        self.creds = None
        
        # Load existing credentials
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                self.creds = pickle.load(token)

        # Refresh or login if needed
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                except Exception as e:
                    logger.error(f"Error refreshing token: {e}")
                    self.creds = None

            if not self.creds:
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(f"Credentials file not found at {self.credentials_path}")
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES)
                self.creds = flow.run_local_server(port=0)

            # Save credentials
            with open(self.token_path, 'wb') as token:
                pickle.dump(self.creds, token)

        # Build services
        self.sheets_service = build('sheets', 'v4', credentials=self.creds)
        self.drive_service = build('drive', 'v3', credentials=self.creds)
        self.forms_service = build('forms', 'v1', credentials=self.creds)
        
        return True

    def list_spreadsheets(self, limit=20):
        """List Google Sheets files from Drive"""
        if not self.drive_service:
            self.authenticate()

        results = self.drive_service.files().list(
            q="mimeType='application/vnd.google-apps.spreadsheet'",
            pageSize=limit,
            fields="nextPageToken, files(id, name, modifiedTime)"
        ).execute()
        
        return results.get('files', [])

    def get_spreadsheet_data(self, spreadsheet_id, range_name='A1:Z1000'):
        """Read data from a spreadsheet"""
        if not self.sheets_service:
            self.authenticate()

        sheet = self.sheets_service.spreadsheets()
        result = sheet.values().get(spreadsheetId=spreadsheet_id,
                                  range=range_name).execute()
        values = result.get('values', [])
        return values

    def get_spreadsheet_metadata(self, spreadsheet_id):
        """Get spreadsheet metadata (sheet names, etc)"""
        if not self.sheets_service:
            self.authenticate()
            
        spreadsheet = self.sheets_service.spreadsheets().get(
            spreadsheetId=spreadsheet_id).execute()
        return spreadsheet

    def create_spreadsheet(self, title, headers=None):
        """Create a new Google Spreadsheet"""
        if not self.sheets_service:
            self.authenticate()
        
        spreadsheet = {
            'properties': {
                'title': title
            }
        }
        
        spreadsheet = self.sheets_service.spreadsheets().create(
            body=spreadsheet,
            fields='spreadsheetId'
        ).execute()
        
        spreadsheet_id = spreadsheet.get('spreadsheetId')
        
        # Add headers if provided
        if headers:
            self.append_to_spreadsheet(spreadsheet_id, [headers])
        
        return spreadsheet_id

    def append_to_spreadsheet(self, spreadsheet_id, values, range_name='A1'):
        """Append data to a spreadsheet"""
        if not self.sheets_service:
            self.authenticate()
        
        body = {
            'values': values
        }
        
        result = self.sheets_service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption='RAW',
            body=body
        ).execute()
        
        return result

    def create_event_form(self, evento_nome, evento_data, evento_duracao):
        """Create a Google Form for event registration"""
        if not self.forms_service:
            self.authenticate()
        
        # Create the form
        form = {
            "info": {
                "title": f"Inscrição - {evento_nome}",
                "documentTitle": f"Inscrição - {evento_nome}",
            }
        }
        
        result = self.forms_service.forms().create(body=form).execute()
        form_id = result['formId']
        
        # Add description
        update = {
            "requests": [
                {
                    "updateFormInfo": {
                        "info": {
                            "description": f"Formulário de inscrição para o evento '{evento_nome}' no dia {evento_data} (duração: {evento_duracao} min)."
                        },
                        "updateMask": "description"
                    }
                },
                # Add Name question
                {
                    "createItem": {
                        "item": {
                            "title": "Nome Completo",
                            "questionItem": {
                                "question": {
                                    "required": True,
                                    "textQuestion": {
                                        "paragraph": False
                                    }
                                }
                            }
                        },
                        "location": {
                            "index": 0
                        }
                    }
                },
                # Add Email question
                {
                    "createItem": {
                        "item": {
                            "title": "Email",
                            "questionItem": {
                                "question": {
                                    "required": True,
                                    "textQuestion": {
                                        "paragraph": False
                                    }
                                }
                            }
                        },
                        "location": {
                            "index": 1
                        }
                    }
                }
            ]
        }
        
        self.forms_service.forms().batchUpdate(
            formId=form_id,
            body=update
        ).execute()
        
        return form_id

    def get_form_responses(self, form_id):
        """Get responses from a Google Form"""
        if not self.forms_service:
            self.authenticate()
        
        result = self.forms_service.forms().responses().list(formId=form_id).execute()
        return result.get('responses', [])

    def link_form_to_sheet(self, form_id):
        """Link a form to a spreadsheet for automatic response collection"""
        # Note: This is done automatically by Google Forms when you click 
        # "Link to Sheets" in the UI. The API doesn't directly support this,
        # but we can create a sheet and sync responses manually.
        pass
