from typing import Any, Generator, Optional
import os
import base64
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload
from google.oauth2.credentials import Credentials
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool


class GoogleDriveFileUpdate(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        Update a file in Google Drive
        """
        file_id = tool_parameters.get("file_id", "")
        name = tool_parameters.get("name", "")
        search_by_name = tool_parameters.get("search_by_name", False)
        
        if search_by_name and not name:
            yield self.create_text_message("Invalid parameter: file name is required when search_by_name is true")
            return
            
        if not file_id and not search_by_name:
            yield self.create_text_message("Invalid parameter: file_id is required when not searching by name")
            return
            
        try:
            if search_by_name:
                file_id = self._find_file_by_name(name)
                if not file_id:
                    yield self.create_text_message(f"File '{name}' not found")
                    return
            
            # Get update parameters
            new_name = tool_parameters.get("new_name", "")
            new_content = tool_parameters.get("new_content", "")
            mime_type = tool_parameters.get("mime_type", "text/plain")
            
            if not new_name and not new_content:
                yield self.create_text_message("Invalid parameters: at least one of new_name or new_content is required")
                return
            
            # Update the file
            self._update_file(file_id, new_name, new_content, mime_type)
            
            update_message = []
            if new_name:
                update_message.append(f"name to '{new_name}'")
            if new_content:
                update_message.append("content")
            
            yield self.create_text_message(f"File updated successfully: {' and '.join(update_message)}")
        except Exception as e:
            yield self.create_text_message(f"Error updating file: {str(e)}")

    def _update_file(self, file_id: str, new_name: str, new_content: str, mime_type: str) -> None:
        """Update a file in Google Drive"""
        credentials = self._get_credentials()
        service = build('drive', 'v3', credentials=credentials)
        
        # If only updating name
        if new_name and not new_content:
            file_metadata = {'name': new_name}
            service.files().update(fileId=file_id, body=file_metadata).execute()
            return
        
        # If updating content (with or without name)
        if new_content:
            # Encode content if it's base64
            try:
                if mime_type.startswith('image/') or mime_type.startswith('application/pdf'):
                    # Try to decode as base64
                    content_bytes = base64.b64decode(new_content)
                else:
                    # Text content
                    content_bytes = new_content.encode('utf-8')
            except:
                # If not base64, treat as text
                content_bytes = new_content.encode('utf-8')
            
            media = MediaInMemoryUpload(content_bytes, mimetype=mime_type)
            
            # If also updating name
            if new_name:
                file_metadata = {'name': new_name}
                service.files().update(
                    fileId=file_id,
                    body=file_metadata,
                    media_body=media
                ).execute()
            else:
                service.files().update(
                    fileId=file_id,
                    media_body=media
                ).execute()
    
    def _find_file_by_name(self, file_name: str) -> Optional[str]:
        """Find a file by name and return its ID"""
        credentials = self._get_credentials()
        service = build('drive', 'v3', credentials=credentials)
        
        query = f"name = '{file_name}' and trashed = false"
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
