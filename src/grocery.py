import random
import os
import httpx
import json
from slack_utils import post_json_to_slack

def get_household_grocery_report(input: str):
    """Generate a household grocery report and post it to Slack."""
    # Example grocery data
    grocery_data = {
        "items": [
            {"name": "rice", "stock": 8, "deficit": 2},
            {"name": "sugar", "stock": 6, "deficit": 4},
            {"name": "wheat", "stock": 7, "deficit": 3}
        ]
    }

    # Format the grocery report for Slack
    formatted_report = format_grocery_report_for_slack(grocery_data)

    # Post the formatted report to Slack
    try:
        post_json_to_slack(formatted_report)
        print("Grocery report posted to Slack successfully.")
    except Exception as e:
        print(f"Failed to post grocery report to Slack: {e}")

    # Return the grocery data
    return grocery_data

def unify_report_format(report: dict, source: str, location: str) -> dict:
    """Unify the report format to a plain JSON structure."""
    return {
        "location": location,
        "items": [
            {
                "name": item["name"].capitalize(),
                "stock": item["stock"],
                "deficit": item["deficit"]
            }
            for item in report["items"]
        ],
        "source": source
    }

def format_grocery_report_for_slack(report):
    """Format the grocery report using the unified report format."""
    return unify_report_format(report, source="inventory_system", location="household")

if __name__ == "__main__":
    # Unit test for get_household_grocery_report
    report = get_household_grocery_report()
    print("Household Grocery Report:")
    for item, details in report.items():
        print(f"Item: {item}, Stock: {details['stock']}, Deficit: {details['deficit']}")

    # Format the report for Slack
    payload = {
        "text": "Household Grocery Report:\n" + "\n".join(
            [f"- {item.capitalize()}: Stock = {details['stock']}, Deficit = {details['deficit']}" for item, details in report.items()]
        )
    }

    # Post the report to Slack
    post_json_to_slack(payload)
