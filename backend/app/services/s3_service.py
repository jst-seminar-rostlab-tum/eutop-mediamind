import asyncio
import io

import boto3
from botocore.exceptions import ClientError

from app.core.config import configs
from app.core.logger import get_logger

logger = get_logger(__name__)


class S3Service:
    _client = boto3.client(
        "s3",
        aws_access_key_id=configs.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=configs.AWS_SECRET_ACCESS_KEY,
        region_name=configs.AWS_REGION,
    )

    @staticmethod
    async def upload_fileobj(
        file_bytes: bytes, bucket: str = None, key: str = ""
    ):
        """
        Uploads an object to S3.
        """
        if bucket is None:
            bucket = configs.AWS_S3_BUCKET_NAME
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            S3Service._client.upload_fileobj,
            io.BytesIO(file_bytes),
            bucket,
            key,
        )

    @staticmethod
    def generate_presigned_url(
        bucket_name: str = None, key: str = "", expires_in: int = 3600
    ) -> str:
        """
        Generates a presigned URL for an S3 object.
        """
        if bucket_name is None:
            bucket_name = configs.AWS_S3_BUCKET_NAME
        try:
            url = S3Service._client.generate_presigned_url(
                "get_object",
                Params={"Bucket": bucket_name, "Key": key},
                ExpiresIn=expires_in,
            )
            return url
        except ClientError as e:
            logger.error(f"Error generating presigned URL: {e}")
            raise RuntimeError(f"Failed to generate presigned URL: {e}")
