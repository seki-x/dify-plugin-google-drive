from typing import Any, Generator, Optional
import os
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool


class GoogleDriveFolderUpdate(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        Update a folder in Google Drive
        """
        folder_id = tool_parameters.get("folder_id", "")
        name = tool_parameters.get("name", "")
        search_by_name = tool_parameters.get("search_by_name", False)
        
        if search_by_name and not name:
            yield self.create_text_message("Invalid parameter: folder name is required when search_by_name is true")
            return
            
        if not folder_id and not search_by_name:
            yield self.create_text_message("Invalid parameter: folder_id is required when not searching by name")
            return
            
        try:
            if search_by_name:
                folder_id = self._find_folder_by_name(name)
                if not folder_id:
                    yield self.create_text_message(f"Folder '{name}' not found")
                    return
            
            new_name = tool_parameters.get("new_name", "")
            if not new_name:
                yield self.create_text_message("Invalid parameter: new_name is required")
                return
                
            self._update_folder(folder_id, new_name)
            yield self.create_text_message(f"Folder updated successfully to '{new_name}'")
        except Exception as e:
            yield self.create_text_message(f"Error updating folder: {str(e)}")

    def _update_folder(self, folder_id: str, new_name: str) -> None:
        """Update a folder in Google Drive"""
        credentials = self._get_credentials()
        service = build('drive', 'v3', credentials=credentials)
        
        file_metadata = {
            'name': new_name
        }
        
        service.files().update(fileId=folder_id, body=file_metadata).execute()
    
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
