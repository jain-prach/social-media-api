from datetime import timedelta
from typing import IO

import boto3
from botocore.exceptions import ClientError

from src.setup.config.settings import settings


class Boto3Service:
    """upload files to AWS Bucket using boto3"""

    def __new__(cls):
        if not settings.AWS_S3_ENDPOINT_URL:
            raise Exception("Storage endpoint url not found!")
        if not settings.AWS_BUCKET_NAME:
            raise Exception("AWS bucket name not found!")
        if not settings.AWS_ACCESS_KEY_ID:
            raise Exception("AWS access_key not found!")
        if not settings.AWS_SECRET_KEY_ID:
            raise Exception("AWS secret_key not found!")
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
        self.bucket_name = settings.AWS_BUCKET_NAME

    def _create_bucket(self, bucket_name: str):
        """create bucket if doesn't exist or prints a list of buckets in existence"""
        bucket_names = [
            bucket["Name"] for bucket in self.__client.list_buckets()["Buckets"]
        ]
        if bucket_name not in bucket_names:
            self.__client.create_bucket(Bucket=bucket_name)
        else:
            print(bucket_names)

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
            print(e)

    def upload_file_from_memory(
        self, object_key: str, file_content: IO, file_type: str
    ) -> None:
        """upload file using IO buffer"""
        try:
            self._create_bucket(self.bucket_name)
            self.__client.put_object(
                Body=file_content,
                Bucket=self.bucket_name,
                Key=object_key,
                ContentType=file_type,
            )
        except ClientError as e:
            print(e)

    def download_file(self, object_key: str, download_path: str) -> None:
        """download file to source path"""
        try:
            self.__client.download_file(
                Bucket=self.bucket_name, Key=object_key, Filename=download_path
            )
        except ClientError as e:
            print(e)

    def download_file_into_memory(self, object_key: str, buffer):
        """download file into memory"""
        try:
            self.__client.download_fileobj(
                Bucket=self.bucket_name, Key=object_key, Fileobj=buffer
            )
        except ClientError as e:
            print(e)
    
    def delete_file(self, object_key:str):
        """delete file using object_key"""
        try:
            self.__client.delete_object(Bucket=self.bucket_name, Key=object_key)
        except ClientError as e:
            print(e)

    def get_presigned_url(self, object_key: str) -> None:
        """get temporary url"""
        try:
            url = self.__client.generate_presigned_url(
                ClientMethod="get_object",
                Params={"Bucket": self.bucket_name, "Key": object_key},
                ExpiresIn=timedelta(**settings.PRESIGNED_URL_TIME).total_seconds(),
            )
            return url
        except ClientError as e:
            print(e)
