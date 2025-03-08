from typing import Any, Generator
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool


class GoogleDriveCreateFolder(Tool):

    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        Create a folder in Google Drive
        """
        # Get parameters
        folder_name = tool_parameters.get("name", "")
        parent_id = tool_parameters.get("parent_id", "root")
        
        if not folder_name:
            yield self.create_text_message("Invalid parameter: folder name is required")
            return
            
        try:
            creds = self._get_credentials()
            folder = self._create_folder(folder_name, parent_id, creds)
            
            yield self.create_json_message({
                "id": folder.get("id"),
                "name": folder.get("name"),
                "parent_id": parent_id,
                "success": True,
                "web_view_link": folder.get("webViewLink", "")
            })
        except Exception as e:
            yield self.create_text_message(f"Error creating folder: {str(e)}")

    def _create_folder(self, name: str, parent_id: str, credentials) -> dict:
        """Create a folder in Google Drive and return its details"""
        service = self._get_drive_service(credentials)
        
        # Prepare folder metadata
        folder_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        
        # Add parent folder if specified
        if parent_id and parent_id != "root":
            folder_metadata['parents'] = [parent_id]
        
        # Create the folder
        folder = service.files().create(
            body=folder_metadata,
            fields='id, name, webViewLink'
        ).execute()
        
        print(f"Folder created: {folder}")
        return folder
    
    def _get_drive_service(self, credentials):
        """Get authenticated Google Drive service"""
        # Create and return the service
        service = build('drive', 'v3', credentials=credentials)
        return service
    
    def _get_credentials(self):
        """Get Google Drive API credentials"""
        # Get credentials from provider
        credentials_json = self.runtime.credentials["credentials_json"]
        
        # Parse the JSON credentials
        try:
            service_account_info = json.loads(credentials_json)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format for credentials_json")
        
        # Validate required fields
        required_fields = ['client_email', 'private_key', 'type']
        missing_fields = [field for field in required_fields if field not in service_account_info]
        if missing_fields:
            raise ValueError(f"Missing required fields in credentials_json: {', '.join(missing_fields)}")
        
        # Create credentials
        creds = service_account.Credentials.from_service_account_info(
            service_account_info, 
            scopes=['https://www.googleapis.com/auth/drive']
        )
        
        return creds
