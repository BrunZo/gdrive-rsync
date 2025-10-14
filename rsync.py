import fs, gdrive, tree

LOCAL_TO_REMOTE = {
  'local': '', # your local folder
  'remote': '' # your remote folder
}

def newest_file_version(local_item: str, remote_item: dict) -> bool:
  """Check if a file has been modified by hash and modification time"""

  if local_item['isFolder'] or remote_item['isFolder']:
    return 'unmodified'
  if local_item['md5Checksum'] == remote_item['md5Checksum']:
    return 'unmodified'

  if local_item['modifiedTime'] > remote_item['modifiedTime']:
    return 'local'
  else:
    return 'remote'

def sync_recursive(service, local_path: str, remote_id: str):
  """Recursively sync a local folder with a Google Drive folder"""
  
  local_items = fs.list_files(local_path)
  remote_items = gdrive.list_files(service, remote_id)
  file_tree = {}

  for local_item in local_items:
    local_item_path = local_path + '/' + local_item
    local_file_deleted = False

    if local_item in remote_items:
      remote_item_id = remote_items[local_item]['id']
      newest_version = newest_file_version(local_items[local_item], remote_items[local_item])
      if newest_version == 'local':
        gdrive.upload_file(service, local_path, local_items[local_item], remote_id)
      elif newest_version == 'remote':
        gdrive.download_file(service, remote_items[local_item]['id'], local_item_path)
      else:
        print(f"File {local_item} is up to date")
    else:
      if tree.local_path_on_previous_sync(local_item_path):
        local_file_deleted = True
        fs.delete_file(local_item_path)
      else:
        remote_item_id = gdrive.upload_file(service, local_path, local_items[local_item], remote_id)

    if not local_file_deleted:
      if local_items[local_item]['isFolder']:
        file_tree[local_item] = {
          'path': local_item_path,
          'id': remote_item_id,
          'children': sync_recursive(service, local_item_path, remote_item_id)
        }
      else:
        file_tree[local_item] = {
          'path': local_item_path,
          'id': remote_item_id,
        }

  for remote_item in remote_items:
    local_item_path = local_path + '/' + remote_item
    remote_item_id = remote_items[remote_item]['id']
    remote_file_deleted = False

    if remote_item not in local_items:
      remote_file_deleted = True
      if tree.remote_id_on_previous_sync(remote_item_id):
        gdrive.delete_file(service, remote_item_id)
      else:
        gdrive.download_file(service, remote_item_id, local_item_path)
    
    if not remote_file_deleted:
      if remote_items[remote_item]['isFolder']:
        file_tree[remote_item] = {
          'path': local_item_path,
          'id': remote_item_id,
          'children': sync_recursive(service, local_item_path, remote_item_id)
        }
      else:
        file_tree[remote_item] = {
          'path': local_item_path,
          'id': remote_item_id,
        }

  return file_tree

def main():
  service = gdrive.auth()
  file_tree = sync_recursive(service, LOCAL_TO_REMOTE['local'], LOCAL_TO_REMOTE['remote'])   
  tree.write_tree(file_tree)

if __name__ == "__main__":
  main()