from typing import Any, Generator, List, Dict
import json
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool


class GoogleDriveFileSearch(Tool):

    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        Search for files in Google Drive
        """
        query = tool_parameters.get("query", "")
        parent_id = tool_parameters.get("parent_id", None)
        file_type = tool_parameters.get("file_type", None)

        if not query:
            yield self.create_text_message("Invalid parameter: search query is required")
            return
            
        max_results = tool_parameters.get("max_results", 10)
        try:
            max_results = int(max_results)
        except ValueError:
            max_results = 10
            
        try:
            creds = self._get_credentials()
            files = self._search_files(query, max_results, creds, parent_id, file_type)
            if not files:
                yield self.create_text_message(f"No files found matching '{query}'")
                return
                
            yield self.create_json_message({
                "file_count": len(files),
                "files": [
                    {
                        "name": file["name"],
                        "id": file["id"],
                        "parent_id": file["parent_id"],
                        "mime_type": file["mime_type"]
                    } for file in files
                ]
            })
        except Exception as e:
            yield self.create_text_message(f"Error searching files: {str(e)}")

    def _search_files(self, query: str, max_results: int, credentials: Credentials, parent_id: str = None, file_type: str = None) -> List[Dict[str, Any]]:
        """Search for files in Google Drive and return their details"""
        service = self._get_drive_service(credentials)
        
        # Build search query for files containing the query string in name
        search_query = f"name contains '{query}' and trashed = false"
        
        # Add file type filter if provided
        if file_type:
            if file_type.lower() == "document":
                search_query += " and mimeType = 'application/vnd.google-apps.document'"
            elif file_type.lower() == "spreadsheet":
                search_query += " and mimeType = 'application/vnd.google-apps.spreadsheet'"
            elif file_type.lower() == "presentation":
                search_query += " and mimeType = 'application/vnd.google-apps.presentation'"
            elif file_type.lower() == "pdf":
                search_query += " and mimeType = 'application/pdf'"
            elif file_type.lower() == "image":
                search_query += " and (mimeType contains 'image/')"
            elif file_type.lower() == "video":
                search_query += " and (mimeType contains 'video/')"
            elif file_type.lower() == "audio":
                search_query += " and (mimeType contains 'audio/')"
        else:
            # Exclude folders by default unless specifically searching for folders
            search_query += " and mimeType != 'application/vnd.google-apps.folder'"
        
        # Add parent folder filter if provided
        if parent_id:
            search_query += f" and '{parent_id}' in parents"
        
        results = []
        page_token = None

        print("Search query:", search_query)
        
        while True:
            response = service.files().list(
                q=search_query,
                spaces='drive',
                fields='nextPageToken, files(id, name, parents, mimeType, createdTime, modifiedTime, webViewLink)',
                pageToken=page_token,
                pageSize=min(max_results, 100)  # API max is 100
            ).execute()
            
            for file in response.get('files', []):
                results.append({
                    'id': file.get('id'),
                    'name': file.get('name'),
                    'parent_id': file.get('parents', ['root'])[0] if file.get('parents') else 'root',
                    'mime_type': file.get('mimeType'),
                    'created_time': file.get('createdTime'),
                    'modified_time': file.get('modifiedTime'),
                    'web_view_link': file.get('webViewLink', '')
                })
                
                if len(results) >= max_results:
                    return results
            
            page_token = response.get('nextPageToken')
            if not page_token:
                break

        print("Results:", results)
                
        return results
    
    def _get_drive_service(self, credentials: Credentials):
        """Get authenticated Google Drive service"""
        print("_get_drive_service:start") 
        # Create and return the service
        service = build('drive', 'v3', credentials=credentials)
        
        print("_get_drive_service:end") 
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
