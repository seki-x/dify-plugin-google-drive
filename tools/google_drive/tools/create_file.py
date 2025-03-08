from typing import Any, Generator
import json
import base64
import requests
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool


class GoogleDriveCreateFile(Tool):

    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        Create a file in Google Drive
        """
        # Get parameters
        file_data = tool_parameters.get("file", {})
        file_name = tool_parameters.get("name", "")
        parent_id = tool_parameters.get("parent_id", "root")
        
        # Debug print
        print(f"File data type: {type(file_data)}")
        print(f"File data: {file_data}")
        
        # Initialize variables
        file_url = ""
        mime_type = ""
        
        # If file data is provided, use its information
        if file_data:
            # Check if file_data is a dictionary or an object
            if isinstance(file_data, dict):
                # Dictionary access
                if not file_name and 'filename' in file_data:
                    file_name = file_data.get('filename')
                
                mime_type = file_data.get('mime_type', '')
                file_url = file_data.get('url', '')
            else:
                # Object attribute access
                try:
                    if not file_name and hasattr(file_data, 'filename'):
                        file_name = file_data.filename
                    
                    if hasattr(file_data, 'mime_type'):
                        mime_type = file_data.mime_type
                        
                    file_url = getattr(file_data, 'url', '')
                except Exception as e:
                    print(f"Error accessing file data attributes: {str(e)}")
                    # Try direct access for common attributes
                    if not file_name:
                        file_name = str(getattr(file_data, 'filename', ''))
                    mime_type = str(getattr(file_data, 'mime_type', ''))
                    file_url = str(getattr(file_data, 'url', ''))
                    
            if not file_url:
                yield self.create_text_message("Error: No file URL provided in file data")
                return
        else:
            yield self.create_text_message("Error: No file data provided")
            return
        
        # Override with explicitly provided mime_type if available
        if tool_parameters.get("mime_type"):
            mime_type = tool_parameters.get("mime_type")
            print(f"Overriding mime_type with explicitly provided value: {mime_type}")
        
        if not file_name:
            yield self.create_text_message("Invalid parameter: file name is required")
            return
            
        if not mime_type:
            # Default to application/octet-stream if mime_type not provided
            mime_type = "application/octet-stream"
            print(f"No mime_type detected, using default: {mime_type}")
            
        try:
            creds = self._get_credentials()
            
            # Download file content from URL
            try:
                print(f"Downloading file from URL: {file_url}")
                response = requests.get(file_url)
                response.raise_for_status()  # Raise exception for non-200 status codes
                file_content = response.content
                print(f"Downloaded file content: {len(file_content)} bytes")
            except Exception as e:
                yield self.create_text_message(f"Error downloading file from URL: {str(e)}")
                return
            
            # Create the file
            file = self._create_file(file_name, parent_id, mime_type, file_content, creds)
            
            yield self.create_json_message({
                "id": file.get("id"),
                "name": file.get("name"),
                "parent_id": parent_id,
                "mime_type": mime_type,
                "success": True,
                "web_view_link": file.get("webViewLink", "")
            })
        except Exception as e:
            yield self.create_text_message(f"Error creating file: {str(e)}")

    def _create_file(self, name: str, parent_id: str, mime_type: str, content: bytes, credentials) -> dict:
        """Create a file in Google Drive and return its details"""
        service = self._get_drive_service(credentials)
        
        # Prepare file metadata
        file_metadata = {
            'name': name,
            'mimeType': mime_type
        }
        
        # Add parent folder if specified
        if parent_id and parent_id != "root":
            file_metadata['parents'] = [parent_id]
        
        # Create media content
        media = MediaInMemoryUpload(content, mimetype=mime_type)
        
        # Create the file
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name, mimeType, webViewLink'
        ).execute()
        
        print(f"File created: {file}")
        return file
    
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
