import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from filebasepy import Filebase

filebase = Filebase(filebase_api_key='', filebase_secret_api_key='')


create = filebase.create_bucket(name='mynewbucket')
print(f"New bucket: {create}")


list_buckets = filebase.list_buckets()
print(f"Bucket(s): {list_buckets}")


upload = filebase.upload_object(path_to_file='/dir/to/file/test.png', name='testpng', bucket='bucketname')
print(f"Upload: {upload}")


upload_metadata = filebase.upload_metadata(data='/dir/to/file/metadata.json', name='mymetadata', bucket='bucketname')
print(f"Upload metadata: {upload_metadata}")


pinned_objects = filebase.list_pinned_objects(bucket='bucketname')
print(f"Pinned objects: {pinned_objects}")


delete = filebase.delete_object(name='myfilename', bucket='bucketname')
print(f"Deleted object: {delete}")