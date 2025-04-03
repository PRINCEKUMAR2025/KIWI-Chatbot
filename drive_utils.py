import os
import io
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class GoogleDriveHandler:
    def __init__(self, credentials_path='credentials.json'):
        """Initialize Google Drive handler with credentials path"""
        self.credentials_path = credentials_path
        self.SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
        self.credentials = None
        self.service = None
        self._authenticate()

    def _authenticate(self):
        """Authenticate with Google Drive"""
        try:
            # Check if credentials file exists
            if not os.path.exists(self.credentials_path):
                logger.error(f"Credentials file not found at {self.credentials_path}")
                return

            # Load credentials from file
            self.credentials = Credentials.from_authorized_user_file(
                self.credentials_path, self.SCOPES)

            # If credentials are invalid or expired, refresh them
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    self.credentials.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, self.SCOPES)
                    self.credentials = flow.run_local_server(port=0)

            # Build the Drive API service
            self.service = build('drive', 'v3', credentials=self.credentials)
            logger.info("Successfully authenticated with Google Drive")

        except Exception as e:
            logger.error(f"Error authenticating with Google Drive: {str(e)}")
            raise

    def download_file(self, file_id):
        """Download a file from Google Drive by its ID"""
        try:
            if not self.service:
                logger.error("Google Drive service not initialized")
                return None

            # Create a file-like object to store the downloaded content
            file = io.BytesIO()
            
            # Download the file
            request = self.service.files().get_media(fileId=file_id)
            downloader = MediaIoBaseDownload(file, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()

            # Read the content
            file.seek(0)
            return file.read().decode('utf-8')

        except Exception as e:
            logger.error(f"Error downloading file from Google Drive: {str(e)}")
            return None

    def get_file_id_from_url(self, url):
        """Extract file ID from Google Drive URL"""
        try:
            # Handle different Google Drive URL formats
            if 'drive.google.com/file/d/' in url:
                return url.split('drive.google.com/file/d/')[1].split('/')[0]
            elif 'drive.google.com/open?id=' in url:
                return url.split('drive.google.com/open?id=')[1].split('&')[0]
            else:
                logger.error("Invalid Google Drive URL format")
                return None
        except Exception as e:
            logger.error(f"Error extracting file ID from URL: {str(e)}")
            return None

    def load_dataset_from_drive(self, file_url):
        """Load dataset from Google Drive URL"""
        try:
            file_id = self.get_file_id_from_url(file_url)
            if not file_id:
                return None

            content = self.download_file(file_id)
            if not content:
                return None

            # Parse JSONL content
            dataset = []
            for line in content.splitlines():
                if line.strip():
                    dataset.append(json.loads(line))

            logger.info(f"Successfully loaded {len(dataset)} entries from Google Drive")
            return dataset

        except Exception as e:
            logger.error(f"Error loading dataset from Google Drive: {str(e)}")
            return None 