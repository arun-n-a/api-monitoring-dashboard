from uuid import uuid4
from typing import List, Dict

import boto3

from app.core.config import settings
from app.core.exceptions import InternalErrorException, NotFoundException

class AmazonServices:
    def __init__(self):
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
        self.bucket_name = settings.S3_BUCKET_NAME
        # self.s3_resource = boto3.resource(
        #     "s3",
        #     aws_access_key_id=Config_is.AWS_ACCESS_KEY_ID,
        #     aws_secret_access_key=Config_is.AWS_SECRET_ACCESS_KEY,
        # )
    
    async def put_object(self, file_is, path: str, content_type: str) -> bool:
        response = self.s3_client.put_object(
            Bucket=settings.S3_BUCKET,
            Key=path,
            Body=file_is,
            ContentType=content_type
            )
        if response.get('ResponseMetadata', {}).get('HTTPStatusCode', 0) != 200:
            raise InternalErrorException()
        return True
    
    async def delete_s3_object(self, path: str) -> bool:
        """
        Delete an object from s3
        """
        self.s3_client.delete_object(Bucket=self.bucket_name, Key=path)
        return True

    async def acl_file_upload_obj_s3(self, file_object, path: str, content_type: str) -> Dict:
        """
        Upload files to s3
        """
        try:
            response = self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=path,
                Body=file_object,
                ACL="public-read",
                ContentType=content_type,
            )
            print(response)
            if response.get("ResponseMetadata", {}).get("HTTPStatusCode", 0) != 200:
                print(response)
                raise InternalErrorException()
        except Exception as e:
            print(f"acl_file_upload_obj_s3 -- {e}")
            raise InternalErrorException()
        return True

    async def get_object_content(self, path: str) -> str:
        """
        Reads and returns the content of an S3 object as a string.
        """
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=path,
            )
            object_content = response['Body'].read().decode('utf-8')
            return object_content
        except Exception as e:
            # Handle specific S3 errors, like the object not existing
            if e.response['Error']['Code'] == 'NoSuchKey':
                print(f"Object not found at path: {path}")
                raise NotFoundException(f"Sorry this changes are not available")
            else:
                print(f"get_object_content -- {e}")
                raise InternalErrorException("An unexpected error occurred. Please try again later")
        except Exception as e:
            print(f"get_object_content -- {e}")
            raise InternalErrorException("An unexpected error occurred. Please try again later")

    # def file_encoded_uploader(
    #     self, file_is: object, image_type: str, file_path: str) -> bool:
    #     """
    #     Upload base64 images to S3 bucket
    #     """
    #     s3_obj = self.s3_resource.Object(Config_is.S3_BUCKET_NAME, file_path)
    #     s3_obj.put(
    #         Body=base64.b64decode(file_is), ContentType=image_type, ACL="public-read"
    #     )
    #     return True


    async def presigned_url(self, file_path: str) -> str:
        response = self.s3_client.generate_presigned_url(
            "get_object", Params={"Bucket": self.bucket_name, "Key": file_path}
        )
        return response

    async def download_s3_object(self, s3_obj_name: str):
        status = self.s3_client.download_file(
            self.bucket_name, s3_obj_name, uuid4().hex
        )
        return status

    async def list_objects(self, prefix: str) -> List:
        objects = self.s3_client.list_objects_v2(
            Bucket=self.bucket_name, Prefix=prefix, Delimiter="/"
        )
        result = []
        for file_object in objects.get("Contents", []):
            key_is = file_object.get("Key")
            if not key_is.endswith("/"):
                url = self.s3_client.generate_presigned_url(
                    ClientMethod="get_object",
                    Params={"Bucket": self.bucket_name, "Key": key_is},
                    ExpiresIn=43200,
                )
                result.append({"name": key_is.split("/")[-1], "url": url})
        return result
