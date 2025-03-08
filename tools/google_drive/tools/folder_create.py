from typing import Any, Generator, Optional
import os
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool


class GoogleDriveFolderCreate(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        Create a folder in Google Drive
        """
        name = tool_parameters.get("name", "")
        if not name:
            yield self.create_text_message("Invalid parameter: folder name is required")
            return

        parent_id = tool_parameters.get("parent_id", "root")
        search_by_name = tool_parameters.get("search_by_name", False)
        
        try:
            if search_by_name and parent_id != "root":
                parent_id = self._find_folder_by_name(parent_id)
                if not parent_id:
                    yield self.create_text_message(f"Parent folder not found by name")
                    return
            
            folder_id = self._create_folder(name, parent_id)
            yield self.create_text_message(f"Folder '{name}' created successfully. Folder ID: {folder_id}")
        except Exception as e:
            yield self.create_text_message(f"Error creating folder: {str(e)}")

    def _create_folder(self, name: str, parent_id: str) -> str:
        """Create a folder in Google Drive and return its ID"""
        credentials = self._get_credentials()
        service = build('drive', 'v3', credentials=credentials)
        
        file_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_id]
        }
        
        folder = service.files().create(body=file_metadata, fields='id').execute()
        return folder.get('id')
    
    def _find_folder_by_name(self, folder_name: str) -> Optional[str]:
        """Find a folder by name and return its ID"""
        credentials = self._get_credentials()
        service = build('drive', 'v3', credentials=credentials)
        
        query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
        items = results.get('files', [])
        
        if items:
            return items[0]['id']
        return None
    
    def _get_credentials(self) -> Credentials:
        """Get Google Drive API credentials"""
        # This is a placeholder for actual credential retrieval logic
        # In a real implementation, this would retrieve credentials from secure storage
        # and handle authentication with Google OAuth2
        token = os.environ.get('GOOGLE_DRIVE_TOKEN')
        if not token:
            raise ValueError("Google Drive token not found in environment variables")
        
        credentials = Credentials.from_authorized_user_info(info=eval(token))
        return credentials
