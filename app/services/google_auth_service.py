"""
Google OAuth Service - Manage Google authentication and API access
"""

import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from flask import session, url_for

# Allow OAuth over HTTP for local development
# WARNING: Only use this for local development, never in production!
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'


class GoogleAuthService:
    """Service to manage Google OAuth authentication"""

    # Required scopes for Forms and Sheets API
    SCOPES = [
        'https://www.googleapis.com/auth/forms.body',
        'https://www.googleapis.com/auth/forms.responses.readonly',
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive.file'
    ]

    def __init__(self, credentials_file='credentials.json'):
        self.credentials_file = credentials_file
        self.token_file = 'token.json'

    def get_credentials(self):
        """Get stored credentials or None"""
        creds = None

        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, self.SCOPES)

        # If credentials are expired or invalid, refresh them
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            self._save_credentials(creds)

        return creds

    def is_authenticated(self):
        """Check if user is authenticated with Google"""
        creds = self.get_credentials()
        return creds is not None and creds.valid

    def get_authorization_url(self, redirect_uri):
        """
        Generate Google OAuth authorization URL

        Args:
            redirect_uri: URL to redirect after authorization

        Returns:
            Authorization URL string
        """
        if not os.path.exists(self.credentials_file):
            raise FileNotFoundError(
                f"Credentials file '{self.credentials_file}' not found. "
                "Please download it from Google Cloud Console."
            )

        flow = Flow.from_client_secrets_file(
            self.credentials_file,
            scopes=self.SCOPES,
            redirect_uri=redirect_uri
        )

        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )

        # Store state in session for verification
        session['oauth_state'] = state

        return authorization_url

    def handle_callback(self, authorization_response, redirect_uri):
        """
        Handle OAuth callback and exchange code for credentials

        Args:
            authorization_response: Full callback URL with code
            redirect_uri: Redirect URI used in authorization

        Returns:
            Credentials object
        """
        state = session.get('oauth_state')

        flow = Flow.from_client_secrets_file(
            self.credentials_file,
            scopes=self.SCOPES,
            state=state,
            redirect_uri=redirect_uri
        )

        flow.fetch_token(authorization_response=authorization_response)

        creds = flow.credentials
        self._save_credentials(creds)

        return creds

    def _save_credentials(self, creds):
        """Save credentials to token file"""
        try:
            # Get absolute path
            token_path = os.path.abspath(self.token_file)
            print(f"DEBUG - Attempting to save token to: {token_path}")
            print(f"DEBUG - Current working directory: {os.getcwd()}")

            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())

            print(f"DEBUG - Token file saved successfully!")
            print(f"DEBUG - File exists after save: {os.path.exists(self.token_file)}")

            # Verify file contents
            if os.path.exists(self.token_file):
                file_size = os.path.getsize(self.token_file)
                print(f"DEBUG - Token file size: {file_size} bytes")
        except Exception as e:
            print(f"ERROR - Failed to save credentials: {str(e)}")
            import traceback
            traceback.print_exc()
            raise

    def revoke_authentication(self):
        """Revoke authentication and delete token file"""
        if os.path.exists(self.token_file):
            os.remove(self.token_file)

    def get_forms_service(self):
        """Get Google Forms API service"""
        creds = self.get_credentials()
        if not creds:
            return None
        return build('forms', 'v1', credentials=creds)

    def get_sheets_service(self):
        """Get Google Sheets API service"""
        creds = self.get_credentials()
        if not creds:
            return None
        return build('sheets', 'v4', credentials=creds)

    def get_drive_service(self):
        """Get Google Drive API service"""
        creds = self.get_credentials()
        if not creds:
            return None
        return build('drive', 'v3', credentials=creds)
