import asyncio
import io

import boto3
from botocore.exceptions import ClientError

from app.core.config import configs
from app.core.logger import get_logger

logger = get_logger(__name__)


class S3Service:
    def __init__(self):
        self.bucket_name: str = configs.AWS_S3_BUCKET_NAME
        self.client = boto3.client(
            "s3",
            aws_access_key_id=configs.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=configs.AWS_SECRET_ACCESS_KEY,
            region_name=configs.AWS_REGION,
        )

    async def upload_fileobj(self, file_bytes: bytes, key: str) -> None:
        """
        Uploads an object to S3.
        """
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            self.client.upload_fileobj,
            io.BytesIO(file_bytes),
            self.bucket_name,
            key,
        )

    async def download_fileobj(self, key: str) -> bytes:
        """
        Downloads an object from S3 and returns its bytes.
        """
        try:
            loop = asyncio.get_event_loop()
            buffer = io.BytesIO()
            await loop.run_in_executor(
                None,
                self.client.download_fileobj,
                self.bucket_name,
                key,
                buffer,
            )
            buffer.seek(0)
            return buffer.read()
        except ClientError as e:
            error_message = (
                f"Failed to download file with key={key} from S3: {e}"
            )
            logger.error(error_message)
            raise Exception(error_message)

    def generate_presigned_url(self, key: str, expires_in: int = 3600) -> str:
        """
        Generates a presigned URL for an S3 object.
        """
        try:
            url = self.client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": key},
                ExpiresIn=expires_in,
            )
            return url
        except ClientError as e:
            logger.error(f"Error generating presigned URL: {e}")
            raise RuntimeError(f"Failed to generate presigned URL: {e}")


# FastAPI dependency
def get_s3_service() -> S3Service:
    return S3Service()
