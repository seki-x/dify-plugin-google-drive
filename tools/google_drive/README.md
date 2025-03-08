# Google Drive ツール

このプラグインは、Google Drive APIを使用してファイルやフォルダを管理するためのDifyツールです。

## 機能

このプラグインには以下の機能が含まれています：

1. **フォルダの作成** - Google Driveに新しいフォルダを作成します
2. **フォルダの更新** - 既存のフォルダ名を変更します
3. **ファイルの作成** - コンテンツと共に新しいファイルを作成します
4. **ファイルの更新** - 既存のファイルの名前や内容を更新します

各ツールは、IDによる直接操作だけでなく、名前による検索機能も提供します。

## セットアップ

1. `.env.example`ファイルを`.env`にコピーし、必要な認証情報を設定します
2. Google Cloud Platformで認証情報を生成するには：
   - [Google Cloud Console](https://console.cloud.google.com/)でプロジェクトを作成
   - Google Drive APIを有効化
   - OAuth 2.0クライアントIDを作成
   - 認証トークンを取得してDify環境変数に設定

## 認証

このツールはOAuth 2.0を使用してGoogle Driveと認証します。トークンは環境変数`GOOGLE_DRIVE_TOKEN`に保存する必要があります。

## 使用方法

### フォルダの作成

```
{
  "name": "新しいフォルダ",
  "parent_id": "root",
  "search_by_name": false
}
```

### フォルダの更新

```
{
  "folder_id": "フォルダID",
  "name": "現在のフォルダ名",
  "search_by_name": true,
  "new_name": "新しいフォルダ名"
}
```

### ファイルの作成

```
{
  "name": "新しいファイル.txt",
  "content": "ファイルの内容",
  "mime_type": "text/plain",
  "parent_id": "フォルダID",
  "search_by_name": false
}
```

### ファイルの更新

```
{
  "file_id": "ファイルID",
  "name": "現在のファイル名",
  "search_by_name": true,
  "new_name": "新しいファイル名",
  "new_content": "新しい内容",
  "mime_type": "text/plain"
}
```
