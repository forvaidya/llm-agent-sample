import requests
import wikipedia
from typing import Dict, Any
from datetime import datetime
from slack_utils import post_to_slack, post_json_to_slack
import logging
from dotenv import load_dotenv
import os
import httpx
import traceback
from grocery import get_household_grocery_report
from weather_utils import fetch_weather_data
import asyncio  # Add this import to handle async calls

# Configure logging
logging.basicConfig(level=logging.INFO)

# Load environment variables from .env file
load_dotenv()

def search_wikipedia(query: str) -> str:
    """Search Wikipedia and return a summary"""
    try:
        return wikipedia.summary(query, sentences=3)
    except:
        return "Could not find Wikipedia article."

def get_current_weather(location: str) -> str:
    """Get current weather for a location (simplified mock version)"""
    return f"Simulated weather for {location}: 72°F, Partly Cloudy"

def calculator(expression: str) -> str:
    """Evaluate a mathematical expression"""
    try:
        return str(eval(expression))
    except Exception as e:
        return f"Error evaluating expression: {e}"

# --- weather api start ---
async def handle_weather_request(location: str) -> str:
    """Handle the entire weather request as a single asynchronous unit."""
    if not location:
        location = "Bangalore"

    try:
        logging.info(f"Attempting to fetch real-time weather data for {location}.")
        # Fetch weather data asynchronously
        weather_data = await fetch_weather_data(location)

        # Post the weather data to Slack
        await post_json_to_slack({
            "location": location,
            "temperature": weather_data["temperature"],
            "condition": weather_data["condition"]
        })

        logging.info(f"Real-time weather data fetched successfully for {location}.")
        return f"Real-time weather in {location}: {weather_data['temperature']}, {weather_data['condition']}"
    except Exception as e:
        logging.error(f"General error occurred: {e}")
        logging.info("Falling back to simulated weather data.")

    # Fallback to simulated data
    logging.info("Falling back to simulated weather data.")
    simulated_temperature = "28C"
    simulated_condition = "Partly Cloudy"
    await post_json_to_slack({
        "location": location,
        "temperature": simulated_temperature,
        "condition": simulated_condition,
        "source": "simulated"
    })
    return f"Simulated weather in {location}: {simulated_temperature}, {simulated_condition}"
# --- weather api end ---

def get_bangalore_bus(route_number: str) -> str:
    """Get Bangalore bus schedule and route information."""
    valid_routes = ["500", "501", "KBS-1", "KBS-2", "BMTC-300"]
    if not route_number.strip():
        return "Please provide a valid Bangalore bus route number."
    if route_number not in valid_routes:
        return f"This route number '{route_number}' is not a valid Bangalore bus route. Valid routes are: {', '.join(valid_routes)}."
    return f"Details for Bangalore bus route {route_number}."

def post_weather_to_slack(location: str, temperature: str, condition: str, source: str):
    """Post weather data to Slack."""
    post_json_to_slack({
        "location": location,
        "temperature": temperature,
        "condition": condition,
        "source": source
    })

# Define our tools
TOOLS = [
    {
        "name": "wikipedia",
        "description": "Search Wikipedia for information. Input should be a search query.",
        "func": search_wikipedia
    },
    {
        "name": "calculator",
        "description": "Evaluate mathematical expressions. Input should be a mathematical expression like '2 + 2'.",
        "func": calculator
    },
    {
        "name": "get_bangalore_weather",
        "description": "Fetch Bangalore weather and post to Slack.",
        "func": handle_weather_request
    },
    {
        "name": "bangalore_bus",
        "description": "Get Bangalore bus schedules and route information. Input should be a route number.",
        "func": get_bangalore_bus
    },
    {
        "name": "get_household_grocery_report",
        "description": "Generate a detailed household grocery report. Use this tool for queries about groceries, stock, or deficits.",
        "func": get_household_grocery_report
    },
]
