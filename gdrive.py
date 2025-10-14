import hashlib
import io
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

import fs
import mime

SCOPES = ["https://www.googleapis.com/auth/drive"]

def auth():
  creds = None
  if os.path.exists("credentials/token.json"):
    creds = Credentials.from_authorized_user_file("credentials/token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials/client_secret.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("credentials/token.json", "w") as token:
      token.write(creds.to_json())

  service = build("drive", "v3", credentials=creds)
  return service

def list_files(service, folder_id: str) -> list:
  results = (
    service.files()
      .list(
        q=f"parents='{folder_id}' and trashed=false", 
        fields="files(id, name, mimeType, size, modifiedTime, md5Checksum)"
      )
      .execute()  
  )
  items = results.get("files", [])
  for item in items:
    item["isFolder"] = item["mimeType"] == "application/vnd.google-apps.folder"
    item["md5Checksum"] = compute_file_checksum(service, item["id"], item["mimeType"])
    extension = mime.extension_for_remote_type(item["mimeType"])
    if extension:
      item["name"] += "." + extension
  return {item["name"]: item for item in items}

def compute_file_checksum(service, file_id: str, mime_type: str) -> str:
  """Compute MD5 checksum by downloading/exporting the file"""
  hash_md5 = hashlib.md5()
  
  try:
    if mime_type.startswith("application/vnd.google-apps"):
      # Export Google Workspace files
      export_mime_type = mime.remote_to_local_type(mime_type)
      request = service.files().export_media(fileId=file_id, mimeType=export_mime_type)
    else:
      # Download regular files
      request = service.files().get_media(fileId=file_id)
    
    # Download to memory and compute hash
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
      status, done = downloader.next_chunk()
    
    # Compute hash from the downloaded content
    fh.seek(0)
    for chunk in iter(lambda: fh.read(4096), b""):
      hash_md5.update(chunk)
    
    return hash_md5.hexdigest()
    
  except Exception as e:
    print(f"Error computing checksum for file {file_id}: {e}")
    return ""

def remove_extension(file_name: str) -> str:
  """Remove the file extension from a filename"""
  return file_name.rsplit('.', 1)[0] if '.' in file_name else file_name

def create_folder(service, folder_name: str, parent_id: str) -> str:
  """Create a folder in Google Drive and return its ID"""
  folder_metadata = {
    "name": folder_name,
    "mimeType": "application/vnd.google-apps.folder",
    "parents": [parent_id]
  }
  folder = service.files().create(body=folder_metadata, fields="id").execute()
  print(f"Created folder: {folder_name}")
  return folder.get("id")

def upload_file(service, path: str, file: dict, parent_id: str) -> None:
  
  if file["isFolder"]:
    new_folder_id = create_folder(service, file["name"], parent_id)
    return new_folder_id

  # Convert Office formats to Google Apps formats for upload
  upload_mime_type = mime.local_to_remote_type(file["mimeType"])
  
  # Remove extension from filename for Google Apps files only
  file_name = file["name"]
  if upload_mime_type.startswith("application/vnd.google-apps"):
    file_name = remove_extension(file["name"])

  file_metadata = {
    "name": file_name,
    "mimeType": upload_mime_type,
    "parents": [parent_id]
  }

  media = MediaFileUpload(path + '/' + file["name"], mimetype=file["mimeType"])
  file = (
    service.files()
      .create(body=file_metadata, media_body=media, fields="id")
      .execute()
  )
  print(f"Uploaded file: {file.get('id')}")
  return file.get('id')

def download_file(service, file_id: str, output_path: str) -> None:

  file = service.files().get(fileId=file_id, fields="mimeType, name").execute()
  file["isFolder"] = file["mimeType"] == "application/vnd.google-apps.folder"
  mime_type = file.get("mimeType")

  if file["isFolder"]:
    fs.create_folder(output_path)
    return

  if mime_type.startswith("application/vnd.google-apps"):
    chosen_mime = mime.remote_to_local_type(mime_type)
    request = (
      service.files()
        .export_media(fileId=file_id, mimeType=chosen_mime)
    )
    fh = io.FileIO(output_path + "." + mime.extension_for_remote_type(chosen_mime), 'wb')
  else:
    request = (
      service.files()
        .get_media(fileId=file_id)
    )
    fh = io.FileIO(output_path, 'wb')

  downloader = MediaIoBaseDownload(fh, request)
  done = False
  while not done:
    status, done = downloader.next_chunk()
  print(f"Downloaded {output_path}")

def delete_file(service, file_id: str) -> None:
  """Delete a file from Google Drive"""
  try:
    service.files().delete(fileId=file_id).execute()
    print(f"Deleted remote file: {file_id}")
  except Exception as e:
    print(f"Error deleting remote file {file_id}: {e}")
