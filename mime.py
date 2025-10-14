EXTENSIONS = {
  "application/pdf": "pdf",
  "application/vnd.google-apps.document": "docx",
  "application/vnd.google-apps.spreadsheet": "xlsx",
  "application/vnd.google-apps.presentation": "pptx",
}

MAP_TYPE = {
  "application/vnd.google-apps.document": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  "application/vnd.google-apps.spreadsheet": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", 
  "application/vnd.google-apps.presentation": "application/vnd.openxmlformats-officedocument.presentationml.presentation"
}

REVERSE_MAP_TYPE = {v: k for k, v in MAP_TYPE.items()}

def extension_for_remote_type(mime_type: str) -> str:
  return EXTENSIONS.get(mime_type, "")

def remote_to_local_type(mime_type: str) -> str:
  return MAP_TYPE.get(mime_type, "application/octet-stream")

def local_to_remote_type(mime_type: str) -> str:
  return REVERSE_MAP_TYPE.get(mime_type, "application/octet-stream")