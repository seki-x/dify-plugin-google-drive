"""
Google Drive utilities module.
Contains common functionality used across Google Drive tools.
"""
import json
from typing import Dict, List, Any, Optional

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaInMemoryUpload


class GoogleDriveUtils:
    """Utilities for Google Drive operations."""

    @staticmethod
    def get_credentials(credentials_json: str) -> service_account.Credentials:
        """
        Get Google Drive API credentials from the provided JSON string
        
        Args:
            credentials_json: Service account credentials JSON string
            
        Returns:
            Google service account credentials object
            
        Raises:
            ValueError: If the JSON is invalid or missing required fields
        """
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
    
    @staticmethod
    def get_drive_service(credentials: service_account.Credentials) -> Any:
        """
        Get authenticated Google Drive service
        
        Args:
            credentials: Google service account credentials
            
        Returns:
            Google Drive service object
        """
        # Create and return the service
        service = build('drive', 'v3', credentials=credentials)
        return service
    
    @staticmethod
    def find_folder_by_name(folder_name: str, credentials: service_account.Credentials, 
                           parent_id: str = "root") -> str:
        """
        Find a folder by name within the specified parent folder
        
        Args:
            folder_name: Name of the folder to find
            credentials: Google service account credentials
            parent_id: ID of the parent folder to search in (default: "root")
            
        Returns:
            Folder ID if found, empty string otherwise
        """
        service = GoogleDriveUtils.get_drive_service(credentials)
        
        # Search for the folder within the specified parent
        query = f"mimeType = 'application/vnd.google-apps.folder' and name = '{folder_name}' and trashed = false"
        
        # Add parent folder constraint if specified (not root)
        if parent_id and parent_id != "root":
            query += f" and '{parent_id}' in parents"
        
        try:
            print(f"Searching for folder with query: {query}")
            response = service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name, parents)',
                pageSize=1
            ).execute()
            
            items = response.get('files', [])
            
            if items:
                return items[0]['id']
        except Exception as e:
            print(f"Error finding folder: {str(e)}")
            
        return ""
    
    @staticmethod
    def create_folder(name: str, parent_id: str, credentials: service_account.Credentials) -> dict:
        """
        Create a folder in Google Drive
        
        Args:
            name: Name of the folder to create
            parent_id: ID of the parent folder (use "root" for Drive root)
            credentials: Google service account credentials
            
        Returns:
            Dictionary with folder details including id, name, webViewLink
        """
        service = GoogleDriveUtils.get_drive_service(credentials)
        
        # Prepare folder metadata
        folder_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        
        # Add parent folder if specified
        if parent_id and parent_id != "root":
            folder_metadata['parents'] = [parent_id]
        else:
            folder_metadata['parents'] = ["root"]
        
        # Create the folder
        try:
            print(f"Creating folder '{name}' with parent ID: {parent_id}")
            folder = service.files().create(
                body=folder_metadata,
                fields='id, name, webViewLink, parents'
            ).execute()
            
            print(f"Folder created: {folder}")
            return folder
        except Exception as e:
            print(f"Error creating folder: {str(e)}")
            return {}
    
    @staticmethod
    def create_file(name: str, parent_id: str, mime_type: str, content: bytes, 
                   credentials: service_account.Credentials) -> dict:
        """
        Create a file in Google Drive
        
        Args:
            name: Name of the file to create
            parent_id: ID of the parent folder (use "root" for Drive root)
            mime_type: MIME type of the file
            content: File content as bytes
            credentials: Google service account credentials
            
        Returns:
            Dictionary with file details including id, name, webViewLink
        """
        service = GoogleDriveUtils.get_drive_service(credentials)
        
        # Prepare file metadata
        file_metadata = {
            'name': name
        }
        
        # Add parent folder if specified
        if parent_id and parent_id != "root":
            file_metadata['parents'] = [parent_id]
        else:
            file_metadata['parents'] = ["root"]
        
        # Create media
        media = MediaInMemoryUpload(content, mimetype=mime_type)
        
        # Create the file
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name, webViewLink, mimeType'
        ).execute()
        
        return file

    @staticmethod
    def search_files(query: str, max_results: int, credentials: service_account.Credentials, 
                     parent_id: Optional[str] = None, file_type: Optional[str] = None) -> List[Dict]:
        """
        Search for files in Google Drive
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            credentials: Google service account credentials
            parent_id: Optional parent folder ID to search within
            file_type: Optional file type filter
            
        Returns:
            List of dictionaries with file details
        """
        service = GoogleDriveUtils.get_drive_service(credentials)
        
        # Build query
        search_query = f"name contains '{query}' and trashed=false"
        
        # Add file type filter if specified
        if file_type:
            if file_type.lower() == "folder":
                search_query += " and mimeType='application/vnd.google-apps.folder'"
            elif file_type.lower() == "document":
                search_query += " and mimeType='application/vnd.google-apps.document'"
            elif file_type.lower() == "spreadsheet":
                search_query += " and mimeType='application/vnd.google-apps.spreadsheet'"
            elif file_type.lower() == "presentation":
                search_query += " and mimeType='application/vnd.google-apps.presentation'"
        
        # Add parent folder filter if specified
        if parent_id:
            search_query += f" and '{parent_id}' in parents"
        
        print(f"Search query: {search_query}")
        
        # Execute search
        response = service.files().list(
            q=search_query,
            spaces='drive',
            fields='files(id, name, mimeType, parents)',
            pageSize=max_results
        ).execute()
        
        # Process results
        results = []
        for file in response.get('files', []):
            parent_id = file.get('parents', ['root'])[0] if 'parents' in file else 'root'
            results.append({
                'id': file.get('id'),
                'name': file.get('name'),
                'mime_type': file.get('mimeType'),
                'parent_id': parent_id
            })
            
        return results
