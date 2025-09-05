import logging
import os
import httpx
import traceback
from typing import Dict, Any
from slack_utils import post_json_to_slack
from dotenv import load_dotenv

# Load environment variables from .env file located parallel to src
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Configure logging
log_level = os.getenv("LOG_LEVEL", "DEBUG").upper()
if log_level == "NONE":
    logging.disable(logging.CRITICAL)  # Disable all logging
else:
    logging.basicConfig(level=log_level)

async def sanitize_location(location: str) -> str:
    """Sanitize the input location to remove unwanted characters or words."""
    sanitized_location = "Bangalore"  # Hardcoded to Bangalore as this function is specific to Bangalore
    logging.debug(f"Sanitized location: {sanitized_location}")
    return sanitized_location

async def fetch_weather_data(location: str) -> Dict[str, Any]:
    """Fetch weather data using multiple APIs."""

    # Sanitize input location
    sanitized_location = await sanitize_location(location)

    async def fetch_from_openweathermap(location: str) -> Dict[str, Any]:
        """Fetch weather data from OpenWeatherMap API."""
        api_key = os.getenv("OPENWEATHER_API_KEY")
        if not api_key:
            logging.debug("OpenWeatherMap API key is not set.")
            raise ValueError("OpenWeatherMap API key is not set.")

        base_url = "http://api.openweathermap.org/data/2.5/weather"
        params = {"q": location, "appid": api_key, "units": "metric"}
        logging.debug(f"Sending request to OpenWeatherMap API for location: {location}")

        async with httpx.AsyncClient() as client:
            response = await client.get(base_url, params=params)
            logging.debug(f"Received response with status code: {response.status_code}")

            if response.status_code == 404:
                logging.debug(f"Location not found: {location}. Please check the input.")
                raise ValueError(f"Location not found: {location}. Please check the input.")

            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as http_err:
                logging.debug(f"HTTP error occurred: {http_err}")
                raise

            data = response.json()
            logging.debug(f"Full API response: {data}")

            # Validate response structure
            if "main" not in data or "temp" not in data["main"]:
                logging.debug(f"Unexpected response structure: {data}")
                raise KeyError("Missing 'main' or 'temp' in API response")

            # Extract temperature safely
            temperature = data["main"].get("temp")
            if temperature is None:
                logging.debug(f"Temperature key is missing in response: {data}")
                raise KeyError("Missing 'temperature' key in API response")

            return {
                "temperature": f"{temperature}C",
                "condition": data.get("weather", [{}])[0].get("description", "Unknown"),
                "source": "openweathermap"
            }

    # Fetch weather data from OpenWeatherMap
    try:
        weather_data = await fetch_from_openweathermap(sanitized_location)
        logging.info("Weather data fetched successfully from OpenWeatherMap.")
    except Exception as e:
        logging.error(f"Failed to fetch weather data from OpenWeatherMap: {e}")
        weather_data = {
            "temperature": "N/A",
            "condition": "N/A",
            "source": "error"
        }

    # Post weather data to Slack
    try:
        await post_json_to_slack(weather_data)
        logging.info("Weather data posted to Slack successfully.")
    except Exception as e:
        logging.error(f"Failed to post weather data to Slack: {e}")

    return weather_data
