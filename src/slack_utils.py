import os
import requests
import json
import logging
from dotenv import load_dotenv
from datetime import datetime
import httpx

# Load environment variables from .env file
load_dotenv()

def post_to_slack(message: str):
    """Post a message to Slack channel defined in .env"""
    slack_channel = os.getenv("SLACK_CHANNEL")
    slack_access_key = os.getenv("SLACK_ACCESS_KEY")
    
    if not slack_channel or not slack_access_key:
        raise ValueError("Slack channel or access key not defined in .env")

    url = "https://slack.com/api/chat.postMessage"
    headers = {
        "Authorization": f"Bearer {slack_access_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "channel": slack_channel,
        "text": message
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.ok:
        print("Message posted successfully!")
        return response.json()
    else:
        raise Exception(f"Failed to post message: {response.text}")

async def post_json_to_slack(json_data: dict):
    """Post a JSON object to Slack channel defined in .env asynchronously."""
    slack_channel = os.getenv("SLACK_CHANNEL")
    slack_access_key = os.getenv("SLACK_ACCESS_KEY")

    if not slack_channel or not slack_access_key:
        logging.error("Slack channel or access key not defined in .env")
        return

    url = "https://slack.com/api/chat.postMessage"
    headers = {
        "Authorization": f"Bearer {slack_access_key}",
        "Content-Type": "application/json"
    }

    # Debug: Log the payload and timestamp
    logging.info(f"Posting to Slack: {json_data}, Timestamp: {datetime.now()}")

    payload = {
        "channel": slack_channel,
        "text": json.dumps(json_data, indent=2)
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            logging.info("Message posted to Slack successfully.")
    except Exception as e:
        logging.error(f"Failed to post message to Slack: {e}")
