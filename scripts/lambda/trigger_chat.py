import email
import json
import os
import urllib.parse
import urllib.request
from email.message import Message
from typing import Any, Dict

import boto3
import redis

S3_CLIENT = boto3.client("s3")
API_HOST = os.environ.get("API_HOST")
if not API_HOST:
    raise RuntimeError("API_HOST environment variable is not set.")
API_URL = f"{API_HOST.rstrip('/')}/api/v1/chatbot/"

API_KEY = os.environ.get("CHAT_API_KEY")
REDIS_URL = os.environ.get("REDIS_URL")
if not REDIS_URL:
    raise RuntimeError("REDIS_URL environment variable is not set.")
redis_client = redis.Redis.from_url(REDIS_URL)

if not API_KEY:
    raise RuntimeError("CHAT_API_KEY environment variable is not set.")


def get_email_body(msg: Message) -> str:
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            if (
                content_type == "text/plain"
                and "attachment" not in content_disposition
            ):
                return part.get_payload(decode=True).decode(
                    part.get_content_charset() or "utf-8",
                    errors="replace",
                )
    else:
        return msg.get_payload(decode=True).decode(
            msg.get_content_charset() or "utf-8",
            errors="replace",
        )
    return ""


def call_api(
    sender: str, subject: str, body: str, api_key: str
) -> None:
    payload = json.dumps(
        {
            "sender": sender,
            "subject": subject,
            "body": body,
        }
    ).encode("utf-8")
    headers = {
        "accept": "application/json",
        "x-api-key": api_key,
        "Content-Type": "application/json",
    }
    req = urllib.request.Request(
        API_URL, data=payload, headers=headers, method="POST"
    )
    try:
        with urllib.request.urlopen(req) as resp:
            resp_body = resp.read().decode()
            print(f"API response: {resp.status} {resp_body}")
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e}")
        raise


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    print("Received event: " + json.dumps(event, indent=2))

    record = event["Records"][0]
    bucket = record["s3"]["bucket"]["name"]
    key = urllib.parse.unquote_plus(
        record["s3"]["object"]["key"], encoding="utf-8"
    )
    # Deduplication check using Redis
    redis_key = f"processed:{key}"
    print(f"Checking Redis for key: {redis_key}")
    if redis_client.get(redis_key):
        print(f"Object {key} already processed (Redis), skipping.")
        return {"statusCode": 200, "body": json.dumps({"status": "skipped"})}

    try:
        print(f"Fetching object from S3: bucket={bucket}, key={key}")
        response = S3_CLIENT.get_object(Bucket=bucket, Key=key)
        raw_email = response["Body"].read().decode("utf-8", errors="replace")
        print(f"Raw email size: {len(raw_email)} bytes")
        msg = email.message_from_string(raw_email)
        sender = msg.get("From")
        subject = msg.get("Subject")
        body = get_email_body(msg)

        print(f"Sender: {sender}")
        print(f"Subject: {subject}")
        print(f"Body (first 500 chars): {body[:500]}")

        try:
            call_api(sender, subject, body, API_KEY)
            print("API call succeeded")
        except Exception as e:
            print(f"API call failed: {e}")
            # Optionally: set Redis key to avoid retrying this object
            redis_client.set(redis_key, "error", ex=86400)
            raise e

        print(f"Setting Redis key {redis_key} as processed (TTL 86400s)")
        redis_client.set(redis_key, "true", ex=86400)

        print("Lambda completed successfully.")
        return {
            "statusCode": 200,
            "body": json.dumps({"status": "ok"}),
        }
    except Exception as e:
        print(f"Exception occurred: {e}")
        print(f"Error getting object {key} from bucket {bucket}:\n{e}")
        raise e
