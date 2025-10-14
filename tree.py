import json

def find_in_dict(search_dict: any, key: str, query: str) -> bool:
  if not isinstance(search_dict, dict):
    return False
  for item in search_dict:
    if search_dict[item].get(key) == query:
      return True
    if find_in_dict(search_dict[item].get('children'), key, query):
      return True
  return False

def local_path_on_previous_sync(local_path: str) -> bool:
  """Check if a file was on the previous sync"""
  with open('file_tree.json', 'r') as f:
    file_tree = json.load(f)
  return find_in_dict(file_tree, 'path', local_path)

def remote_id_on_previous_sync(remote_id: str) -> bool:
  """Check if a file was on the previous sync"""
  with open('file_tree.json', 'r') as f:
    file_tree = json.load(f)
  return find_in_dict(file_tree, 'id', remote_id)

def write_tree(file_tree: dict) -> None:
  with open('file_tree.json', 'w') as f:
    json.dump(file_tree, f)