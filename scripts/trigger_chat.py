import json
import urllib.parse
import boto3
import email
import urllib.request
import os
from typing import Any, Dict

S3_CLIENT = boto3.client("s3")
API_URL = "https://api.mediamind.csee.tech/api/v1/chatbot/"


def get_email_body(msg: email.message.Message) -> str:
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            if content_type == "text/plain" and "attachment" not in content_disposition:
                return part.get_payload(decode=True).decode(
                    part.get_content_charset() or "utf-8", errors="replace"
                )
    else:
        return msg.get_payload(decode=True).decode(
            msg.get_content_charset() or "utf-8", errors="replace"
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
    headers = {"Content-Type": "application/json", "x-api-key": api_key}
    req = urllib.request.Request(API_URL, data=payload, headers=headers, method="POST")
    with urllib.request.urlopen(req) as resp:
        resp_body = resp.read().decode()
        print(f"API response: {resp.status} {resp_body}")


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    print("Received event: " + json.dumps(event, indent=2))
    api_key = os.environ.get("CHAT_API_KEY")
    if not api_key:
        raise RuntimeError("CHAT_API_KEY environment variable is not set.")

    record = event["Records"][0]
    bucket = record["s3"]["bucket"]["name"]
    key = urllib.parse.unquote_plus(record["s3"]["object"]["key"], encoding="utf-8")

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

        call_api(sender, subject, body, key, bucket, api_key)

        return {
            "statusCode": 200,
            "body": json.dumps("Email processed and sent to API."),
        }
    except Exception as e:
        print(e)
        print(f"Error getting object {key} from bucket {bucket}:\n{e}")
        raise e
