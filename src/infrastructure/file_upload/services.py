from datetime import timedelta
from typing import IO, Optional

import boto3
from botocore.exceptions import ClientError

from src.setup.config.settings import settings
from lib.fastapi.custom_enums import Environment
<<<<<<< HEAD
=======
from lib.fastapi.custom_exceptions import CustomException
>>>>>>> db81b47e93c4576a973deb70e666e05a70868fe3


class Boto3Service:
    """upload files to AWS Bucket using boto3"""

    def __new__(cls):
        if not settings.AWS_S3_ENDPOINT_URL:
            raise CustomException(detail="Storage endpoint url not found!")
        if not settings.AWS_BUCKET_NAME:
            raise CustomException(detail="AWS bucket name not found!")
        if not settings.AWS_ACCESS_KEY_ID:
            raise CustomException(detail="AWS access_key not found!")
        if not settings.AWS_SECRET_KEY_ID:
            raise CustomException(detail="AWS secret_key not found!")
        if not hasattr(cls, "instance"):
            cls.instance = super(Boto3Service, cls).__new__(cls)
        return cls.instance

    def __init__(self) -> None:
        self.__client = boto3.client(
            "s3",
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_KEY_ID,
            verify=False,
            # region_name=settings.AWS_S3_REGION_NAME,
        )
        if settings.ENVIRONMENT != Environment.TESTING.value:
            self.bucket_name = settings.AWS_BUCKET_NAME
        else:
            self.bucket_name = settings.TEST_AWS_BUCKET_NAME

    def _create_bucket(self, bucket_name: str) -> None:
        """create bucket if doesn't exist or prints a list of buckets in existence"""
        bucket_names = [
            bucket["Name"] for bucket in self.__client.list_buckets()["Buckets"]
        ]
        if bucket_name not in bucket_names:
            self.__client.create_bucket(Bucket=bucket_name)
        # print(bucket_names)
        return None

    def upload_file_from_source(
        self, object_key: str, source_file: str, content_type: str
    ) -> None:
        """upload file from source"""
        try:
            self._create_bucket(self.bucket_name)
            self.__client.upload_file(
                Filename=source_file,
                Bucket=self.bucket_name,
                Key=object_key,
                ExtraArgs={"ContentType": content_type},
            )
        except ClientError as e:
            raise CustomException(detail=f"Client Error in Boto3: {e}")

    def upload_file_from_memory(
        self, object_key: str, file_content: IO, file_type: str
    ) -> None:
        """upload file using IO buffer"""
        try:
            self._create_bucket(self.bucket_name)
            # print(object_key, file_content, file_type)
            self.__client.put_object(
                Body=file_content,
                Bucket=self.bucket_name,
                Key=object_key,
                ContentType=file_type,
            )
        except ClientError as e:
            raise CustomException(detail=f"Client Error in Boto3: {e}")

    def download_file(self, object_key: str, download_path: str) -> None:
        """download file to source path"""
        try:
            self.__client.download_file(
                Bucket=self.bucket_name, Key=object_key, Filename=download_path
            )
        except ClientError as e:
            raise CustomException(detail=f"Client Error in Boto3: {e}")

    def download_file_into_memory(self, object_key: str, buffer):
        """download file into memory"""
        try:
            self.__client.download_fileobj(
                Bucket=self.bucket_name, Key=object_key, Fileobj=buffer
            )
        except ClientError as e:
            print(e)

    def delete_file(self, object_key: str) -> None:
        """delete file using object_key"""
        try:
            self.__client.delete_object(Bucket=self.bucket_name, Key=object_key)
        except ClientError as e:
            raise CustomException(detail=f"Client Error in Boto3: {e}")

    def get_presigned_url(self, object_key: str) -> Optional[str]:
        """get temporary url"""
        try:
            url = self.__client.generate_presigned_url(
                ClientMethod="get_object",
                Params={"Bucket": self.bucket_name, "Key": object_key},
                ExpiresIn=timedelta(**settings.PRESIGNED_URL_TIME).total_seconds(),
            )
            return url
        except ClientError as e:
<<<<<<< HEAD
            print(e)
=======
            raise CustomException(detail=f"Client Error in Boto3: {e}")
>>>>>>> db81b47e93c4576a973deb70e666e05a70868fe3

    def delete_bucket(self, bucket_name: str) -> None:
        """delete s3 bucket after emptying its content"""
        try:
            bucket_names = [
                bucket["Name"] for bucket in self.__client.list_buckets()["Buckets"]
            ]
            if bucket_name in bucket_names:
                objects = self.__client.list_objects_v2(Bucket=bucket_name)
                for obj in objects["Contents"]:
                    self.__client.delete_object(Bucket=bucket_name, Key=obj["Key"])
                self.__client.delete_bucket(Bucket=bucket_name)
        except ClientError as e:
<<<<<<< HEAD
            print(e)
=======
            raise CustomException(detail=f"Client Error in Boto3: {e}")
>>>>>>> db81b47e93c4576a973deb70e666e05a70868fe3
