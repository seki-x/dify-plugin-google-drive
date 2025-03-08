from typing import Any
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from dify_plugin import ToolProvider
from tools.folder_create import GoogleDriveFolderCreate
from tools.folder_update import GoogleDriveFolderUpdate
from tools.file_create import GoogleDriveFileCreate
from tools.file_update import GoogleDriveFileUpdate


class GoogleDriveProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            # Attempt to list files to validate credentials
            GoogleDriveFolderCreate().invoke(tool_parameters={"name": "test_folder", "parent_id": "root"})
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
