"""
Non-official Python library for Filebase
Built by: KusamaHub
"""
import json
import boto3
import base64
import typing as tp
import requests

# Custom tpe hints
ResponsePayload = tp.Dict[str, tp.Any]
OptionsDict = tp.Dict[str, tp.Any]
Headers = tp.Dict[str, str]

# global constants
API_ENDPOINT: str = "https://api.filebase.io/v1/"
AWS_ENDPOINT: str = "https://s3.filebase.com"


class Filebase:
    """A Filebase API/S3 client session object"""

    def __init__(self, filebase_api_key: str, filebase_secret_api_key: str) -> None:
        self.filebase_api_key = filebase_api_key
        self.filebase_secret_api_key = filebase_secret_api_key
        self.s3 = boto3.client('s3',
                               endpoint_url=AWS_ENDPOINT,
                               aws_access_key_id=self.filebase_api_key,
                               aws_secret_access_key=self.filebase_secret_api_key)

    @staticmethod
    def handle_error(response):
        """
        Handle error from response
        """
        if isinstance(response, dict):
            return {"status": response['ResponseMetadata']['HTTPStatusCode'], "reason": response['ResponseMetadata']['HTTPStatusCode'], "text": response}
        else:
            return {"status": response.status_code, "reason": response.reason, "text": response.text}

    def create_bucket(self, name: str):
        """
        Creates an S3 bucket with the given name.

        Parameters:
            name (str): The name of the bucket to be created.

        Returns:
            Dict[str, Any] if the request is successful, containing the entire response.
            Exception if there is an error.
        """
        try:
            response = self.s3.create_bucket(Bucket=name.lower())
            return response if response['ResponseMetadata']['HTTPStatusCode'] == 200 else self.handle_error(response)
        except Exception as error:
            return error

    def list_pinned_objects(self, bucket: str):
        """
        Retrieve a list of pinned objects in JSON format.

        Returns:
            dict: A dictionary containing the JSON data of the pinned objects,
                  if the GET request is successful.
            dict: A dictionary containing the error details, if the GET request
                  is not successful.
            Exception: The error encountered, in case of any other exception
        """
        base64encoded = base64.b64encode(bytes(f"{self.filebase_api_key}:{self.filebase_secret_api_key}:{bucket}", 'utf-8')).decode('utf-8')
        _auth_headers: Headers = {
            "Authorization": f"Bearer {base64encoded}"
        }

        url: str = API_ENDPOINT + "ipfs/pins"
        headers: Headers = _auth_headers
        headers["Content-Type"] = "application/json"

        try:
            response: requests.Response = requests.get(url=url, headers=headers)
            return response.json() if response.ok else self.handle_error(response)
        except Exception as error:
            return error

    def list_buckets(self):
        """
        Retrieve a list of all S3 buckets in the AWS account.

        Returns:
            list: A list of dictionaries containing the details of the S3 buckets,
                  if the request is successful.
            dict: A dictionary containing the error details, if the request
                  is not successful.
            Exception: The error encountered, in case of any other exception

        """
        try:
            response = self.s3.list_buckets()
            return response['Buckets'] if response['ResponseMetadata']['HTTPStatusCode'] == 200 else self.handle_error(response)
        except Exception as error:
            return error

    def upload_object(self, path_to_file: str, name: str, bucket: str):
        """
        Upload a file to Filebase using Amazon S3 service.

        Args:
        - path_to_file (str): The file path of the file to be uploaded.
        - name (str): The name to be given to the uploaded file in the bucket.
        - bucket (str): The name of the bucket to which the file is to be uploaded.

        Returns:
        - CID: A string representing the Content-ID of the uploaded file.
          If the upload is successful.
        - error: An error message if the upload fails.

        Example:
        - upload_object('/path/to/file.txt', 'file_name', 'my-bucket')
        """
        try:
            file = open(path_to_file, 'rb')
            response = self.s3.put_object(Body=file, Bucket=bucket.lower(), Key=name)
            return response['ResponseMetadata']['HTTPHeaders']['x-amz-meta-cid'] if response['ResponseMetadata']['HTTPStatusCode'] == 200 else self.handle_error(response)
        except Exception as error:
            return error

    def delete_object(self, name: str, bucket: str):
        """
        Delete an object from S3 bucket

        Parameters:
            - name (str): The name/key of the object to be deleted
            - bucket (str): The name of the bucket where the object is located

        Returns:
            - Dict: metadata of the deleted object if successful
            - str: error message if the deletion failed or an exception is thrown
        """
        try:
            response = self.s3.delete_object(Bucket=bucket.lower(), Key=name)
            return response if response['ResponseMetadata']['HTTPStatusCode'] == 200 else self.handle_error(response)
        except Exception as error:
            return error

    def upload_metadata(self, data: tp.Any, name:  str, bucket: str):
        """
        Uploads metadata as a JSON object to a specified S3 bucket using the `boto3` library.

        Args:
            data (tp.Any): The metadata to be uploaded.
            name (str): The key for the object in the S3 bucket.
            bucket (str): The S3 bucket name.

        Returns:
            Union[str, Exception]: The CID of the uploaded object if the request is successful, or an Exception if an error occurs.
        """
        try:
            encoded_metadata = json.dumps(data, indent=4).encode('utf-8')
            response = self.s3.put_object(Body=encoded_metadata, Bucket=bucket.lower(), Key=name)
            return response['ResponseMetadata']['HTTPHeaders']['x-amz-meta-cid'] if response['ResponseMetadata']['HTTPStatusCode'] == 200 else self.handle_error(response)
        except Exception as error:
            return error
