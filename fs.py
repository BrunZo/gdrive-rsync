import os
import datetime
import hashlib
import mimetypes

def file_tree(folder_path: str) -> list:
  """Get all files in a folder and its subfolders"""
  pass

def list_files(folder_path: str) -> list:
  """Get all files in a folder"""
  items = os.listdir(folder_path)
  result = {}
  
  for item in items:
    item_path = os.path.join(folder_path, item)    
    is_folder = os.path.isdir(item_path)
    mime_type = mimetypes.guess_type(item_path)[0] or 'application/octet-stream'
    
    result[item] = {
      "name": item,
      "isFolder": is_folder,
      "mimeType": mime_type,
      "size": os.path.getsize(item_path),
      "modifiedTime": datetime.datetime.fromtimestamp(os.path.getmtime(item_path)).isoformat() + "Z",
      "md5Checksum": file_hash(item_path) if not is_folder else None
    }
  return result

def file_hash(file_path: str) -> str:
  """Calculate MD5 hash of a local file"""
  hash_md5 = hashlib.md5()
  try:
    with open(file_path, "rb") as f:
      for chunk in iter(lambda: f.read(4096), b""):
        hash_md5.update(chunk)
    return hash_md5.hexdigest()
  except Exception as e:
    print(f"Error calculating hash for {file_path}: {e}")
    return ""

def create_folder(folder_path: str) -> None:
  """Create a folder"""
  os.makedirs(folder_path, exist_ok=True)

def delete_file(file_path: str) -> None:
  """Delete a file"""
  pass