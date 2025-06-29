# Google Drive Tools

**Author:** yoshiki-0428  
**Version:** 0.1.0  
**Type:** tool  

## Description

This plugin provides a set of tools for integrating Google Drive with Dify applications. It allows you to search, create, and manage files and folders in Google Drive directly from your Dify workflows and agents.

## Tools Included

1. **File Search** - Search for files in Google Drive by name
2. **Folder Search** - Find folders in Google Drive by name
3. **Create File** - Upload files to Google Drive
4. **Create Folder** - Create new folders in Google Drive
5. **File Download** - Download files from Google Drive (Google Workspace files are automatically exported to PDF before download)

## Setup

### Prerequisites

- A Google Cloud Platform account
- A Google Cloud project with the Google Drive API enabled
- A service account with appropriate permissions for Google Drive

### Creating a Service Account

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Drive API for your project
4. Create a service account:
   - Go to "IAM & Admin" > "Service Accounts"
   - Click "Create Service Account"
   - Give it a name and description
   - Grant it appropriate roles (at least "Drive File Creator" and "Drive Viewer")
   - Click "Create"
5. Create a key for the service account:
   - Click on the service account you just created
   - Go to the "Keys" tab
   - Click "Add Key" > "Create new key"
   - Choose JSON format and click "Create"
   - Save the downloaded JSON file securely

### Configuration in Dify

1. In your Dify application, go to the Plugins section
2. Find and install the Google Drive plugin
3. When configuring the plugin, you'll need to provide:
   - **credentials_json**: The entire content of the service account JSON key file

## Usage Examples

### Search for Files

Use the File Search tool to find files in Google Drive by name:

```
Input:
{
  "query": "quarterly report",
  "max_results": 5,
  "parent_id": "optional_folder_id"
}

Output:
{
  "file_count": 2,
  "files": [
    {
      "id": "1AbCdEfGhIjKlMnOpQrStUvWxYz",
      "name": "Q1 Quarterly Report.pdf",
      "mime_type": "application/pdf",
      "web_view_link": "https://drive.google.com/file/d/1AbCdEfGhIjKlMnOpQrStUvWxYz/view"
    },
    {
      "id": "2BcDeFgHiJkLmNoPqRsTuVwXyZ",
      "name": "Q2 Quarterly Report.docx",
      "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      "web_view_link": "https://drive.google.com/file/d/2BcDeFgHiJkLmNoPqRsTuVwXyZ/view"
    }
  ]
}
```

### Create a Folder

Use the Create Folder tool to create a new folder in Google Drive:

```
Input:
{
  "name": "Project Documents",
  "parent_id": "optional_parent_folder_id"
}

Output:
{
  "id": "3CdEfGhIjKlMnOpQrStUvWxYz",
  "name": "Project Documents",
  "web_view_link": "https://drive.google.com/drive/folders/3CdEfGhIjKlMnOpQrStUvWxYz",
  "success": true
}
```

### Upload a File

Use the Create File tool to upload a file to Google Drive:

```
Input:
{
  "file": {file_object},
  "name": "presentation.pptx",
  "folder_name": "Project Presentations"
}

Output:
{
  "id": "4DeFgHiJkLmNoPqRsTuVwXyZ",
  "name": "presentation.pptx",
  "parent_id": "5EfGhIjKlMnOpQrStUvWxYz",
  "folder_name": "Project Presentations",
  "mime_type": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
  "web_view_link": "https://drive.google.com/file/d/4DeFgHiJkLmNoPqRsTuVwXyZ/view",
  "success": true
}
```

### Download a File

Use the File Download tool to download a file by its ID. Google Workspace documents (Docs, Sheets, Slides, etc.) are exported to PDF automatically.

```
Input:
{
  "file_id": "1AbCdEfGhIjKlMnOpQrStUvWxYz"
}

Output (binary file example):
{
  "text": "File 'sample.xlsx' downloaded successfully",
  "files": [
    {
      "dify_model_identity": "__dify__file__",
      "id": null,
      "tenant_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
      "type": "document",
      "transfer_method": "tool_file",
      "remote_url": null,
      "related_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
      "filename": "abc123def456789012345678901234567.xlsx",
      "extension": ".xlsx",
      "mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      "size": 1291183,
      "url": "https://upload.dify.ai/files/tools/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.xlsx?timestamp=1234567890&nonce=abcdef1234567890abcdef1234567890&sign=ExampleSignatureHashValue123456789abcdef"
    }
  ],
  "json": [
    {
      "exported": false,
      "file_id": "1AbCdEfGhIjKlMnOpQrStUvWxYz",
      "file_name": "sample.xlsx",
      "file_size": 1291183,
      "mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    }
  ]
}

Output (Google Doc example):
{
  "text": "Google Workspace file 'sample-gdoc' exported as PDF 'sample-gdoc.pdf' successfully",
  "files": [
    {
      "dify_model_identity": "__dify__file__",
      "id": null,
      "tenant_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
      "type": "document",
      "transfer_method": "tool_file",
      "remote_url": null,
      "related_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
      "filename": "def456abc789012345678901234567890.pdf",
      "extension": ".pdf",
      "mime_type": "application/pdf",
      "size": 14687,
      "url": "https://upload.dify.ai/files/tools/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx.pdf?timestamp=1234567891&nonce=fedcba0987654321fedcba0987654321&sign=AnotherExampleSignatureHashValue987654321abcdef"
    }
  ],
  "json": [
    {
      "exported": true,
      "file_id": "2BcDeFgHiJkLmNoPqRsTuVwXyZ",
      "file_name": "sample-gdoc.pdf",
      "file_size": 14687,
      "mime_type": "application/pdf",
      "original_mime_type": "application/vnd.google-apps.document",
      "original_name": "sample-gdoc"
    }
  ]
}
```

## Permissions and Security

- The tools operate with the permissions of the service account you configured
- To access user-specific files, you'll need to share those files with the service account email
- For shared drives, the service account needs to be added as a member of the shared drive

## Troubleshooting

If you encounter issues:

1. Verify that the Google Drive API is enabled in your Google Cloud project
2. Check that the service account has the necessary permissions
3. Ensure the credentials JSON is correctly formatted and complete
4. For "File not found" errors, verify that the file exists and is accessible to the service account

## Support

For issues or feature requests, please open an issue in the [Dify Official Plugins repository](https://github.com/langgenius/dify-official-plugins).
