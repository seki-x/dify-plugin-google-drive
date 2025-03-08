from typing import Any, Generator, Optional
import os
import base64
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload
from google.oauth2.credentials import Credentials
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool


class GoogleDriveFileCreate(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        Create a file in Google Drive
        """
        name = tool_parameters.get("name", "")
        if not name:
            yield self.create_text_message("Invalid parameter: file name is required")
            return

        content = tool_parameters.get("content", "")
        if not content:
            yield self.create_text_message("Invalid parameter: content is required")
            return

        mime_type = tool_parameters.get("mime_type", "text/plain")
        parent_id = tool_parameters.get("parent_id", "root")
        search_by_name = tool_parameters.get("search_by_name", False)
        
        try:
            if search_by_name and parent_id != "root":
                parent_id = self._find_folder_by_name(parent_id)
                if not parent_id:
                    yield self.create_text_message(f"Parent folder not found by name")
                    return
            
            file_id = self._create_file(name, content, mime_type, parent_id)
            yield self.create_text_message(f"File '{name}' created successfully. File ID: {file_id}")
        except Exception as e:
            yield self.create_text_message(f"Error creating file: {str(e)}")

    def _create_file(self, name: str, content: str, mime_type: str, parent_id: str) -> str:
        """Create a file in Google Drive and return its ID"""
        credentials = self._get_credentials()
        service = build('drive', 'v3', credentials=credentials)
        
        # Encode content if it's base64
        try:
            if mime_type.startswith('image/') or mime_type.startswith('application/pdf'):
                # Try to decode as base64
                content_bytes = base64.b64decode(content)
            else:
                # Text content
                content_bytes = content.encode('utf-8')
        except:
            # If not base64, treat as text
            content_bytes = content.encode('utf-8')
        
        media = MediaInMemoryUpload(content_bytes, mimetype=mime_type)
        
        file_metadata = {
            'name': name,
            'parents': [parent_id]
        }
        
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        
        return file.get('id')
    
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
