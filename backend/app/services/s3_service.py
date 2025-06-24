import asyncio
import io

import boto3
from botocore.exceptions import ClientError

from app.core.config import configs
from app.core.logger import get_logger

logger = get_logger(__name__)


class S3Service:
    def __init__(
        self,
        aws_access_key_id=None,
        aws_secret_access_key=None,
        aws_region=None,
        bucket_name=None,
    ):
        self.aws_access_key_id = aws_access_key_id or configs.AWS_ACCESS_KEY_ID
        self.aws_secret_access_key = (
            aws_secret_access_key or configs.AWS_SECRET_ACCESS_KEY
        )
        self.aws_region = aws_region or configs.AWS_REGION
        self.bucket_name = bucket_name or configs.AWS_S3_BUCKET_NAME
        self.client = boto3.client(
            "s3",
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            region_name=self.aws_region,
        )

    async def upload_fileobj(
        self, file_bytes: bytes, bucket: str | None = None, key: str = ""
    ):
        """
        Uploads an object to S3.
        """
        bucket = bucket or self.bucket_name
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            self.client.upload_fileobj,
            io.BytesIO(file_bytes),
            bucket,
            key,
        )

    def generate_presigned_url(
        self, bucket_name: str = None, key: str = "", expires_in: int = 3600
    ) -> str:
        """
        Generates a presigned URL for an S3 object.
        """
        bucket_name = bucket_name or self.bucket_name
        try:
            url = self.client.generate_presigned_url(
                "get_object",
                Params={"Bucket": bucket_name, "Key": key},
                ExpiresIn=expires_in,
            )
            return url
        except ClientError as e:
            logger.error(f"Error generating presigned URL: {e}")
            raise RuntimeError(f"Failed to generate presigned URL: {e}")


# FastAPI dependency
def get_s3_service():
    return S3Service()
