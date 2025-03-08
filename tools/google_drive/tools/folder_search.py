from typing import Any, Generator, List, Dict
import json
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool


class GoogleDriveFolderSearch(Tool):

    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        Search for folders in Google Drive
        """
        query = tool_parameters.get("query", "")
        parent_id = tool_parameters.get("parent_id", None)

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
            folders = self._search_folders(query, max_results, creds, parent_id)
            if not folders:
                yield self.create_text_message(f"No folders found matching '{query}'")
                return
                
            yield self.create_json_message({
                "folder_count": len(folders),
                "folders": [
                    {
                        "name": folder["name"],
                        "id": folder["id"],
                        "parent_id": folder["parent_id"]
                    } for folder in folders
                ]
            })
        except Exception as e:
            yield self.create_text_message(f"Error searching folders: {str(e)}")

    def _search_folders(self, query: str, max_results: int, credentials: Credentials, parent_id: str = None) -> List[Dict[str, Any]]:
        """Search for folders in Google Drive and return their details"""
        service = self._get_drive_service(credentials)
        
        # Build search query for folders containing the query string in name
        search_query = f"mimeType = 'application/vnd.google-apps.folder' and name contains '{query}' and trashed = false"
        
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
                fields='nextPageToken, files(id, name, parents, createdTime, modifiedTime)',
                pageToken=page_token,
                pageSize=min(max_results, 100)  # API max is 100
            ).execute()
            
            for file in response.get('files', []):
                results.append({
                    'id': file.get('id'),
                    'name': file.get('name'),
                    'parent_id': file.get('parents', ['root'])[0] if file.get('parents') else 'root',
                    'created_time': file.get('createdTime'),
                    'modified_time': file.get('modifiedTime')
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
        # Access credentials from environment variables or provider credentials
        print("_get_drive_service:start") 
        # Create and return the service
        service = build('drive', 'v3', credentials=credentials)
        
        print("_get_drive_service:end") 
        return service
    
    def _get_credentials(self) -> Credentials:
        """Get Google Drive API credentials"""
        print("_get_credentials:start")
        
        # Parse the JSON credentials
        try:
            credentials_json = self.runtime.credentials["credentials_json"]
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
