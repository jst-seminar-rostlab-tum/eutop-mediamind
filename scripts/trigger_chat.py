import email
import json
import os
import urllib.parse
import urllib.request
from email.message import Message
from typing import Any, Dict

import boto3

S3_CLIENT = boto3.client("s3")
API_HOST = os.environ.get("API_HOST")
if not API_HOST:
    raise RuntimeError("API_HOST environment variable is not set.")
API_URL = f"{API_HOST.rstrip('/')}/api/v1/chatbot/"

API_KEY = os.environ.get("CHAT_API_KEY")
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
    sender: str, subject: str, body: str, key: str, bucket: str, api_key: str
) -> None:
    payload = json.dumps(
        {
            "sender": sender,
            "subject": subject,
            "body": body,
            "s3_key": key,
            "bucket": bucket,
        }
    ).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
    }
    req = urllib.request.Request(
        API_URL, data=payload, headers=headers, method="POST"
    )
    with urllib.request.urlopen(req) as resp:
        resp_body = resp.read().decode()
        print(f"API response: {resp.status} {resp_body}")


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    print("Received event: " + json.dumps(event, indent=2))

    record = event["Records"][0]
    bucket = record["s3"]["bucket"]["name"]
    key = urllib.parse.unquote_plus(
        record["s3"]["object"]["key"], encoding="utf-8"
    )
    try:
        response = S3_CLIENT.get_object(Bucket=bucket, Key=key)
        raw_email = response["Body"].read().decode("utf-8", errors="replace")
        msg = email.message_from_string(raw_email)
        sender = msg.get("From")
        subject = msg.get("Subject")
        body = get_email_body(msg)

        print(f"Sender: {sender}")
        print(f"Subject: {subject}")
        print(f"Body (first 500 chars): {body[:500]}")

        call_api(sender, subject, body, key, bucket, API_KEY)

        return {
            "statusCode": 200,
            "body": json.dumps("Email processed and sent to API."),
        }
    except Exception as e:
        print(e)
        print(f"Error getting object {key} from bucket {bucket}:\n{e}")
        raise e
