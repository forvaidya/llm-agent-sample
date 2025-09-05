import json
from typing import List, Dict, Any, Callable, Optional
from dataclasses import dataclass
from api_client import OpenRouterClient
import os
import httpx
from dotenv import load_dotenv
import asyncio

@dataclass
class Tool:
    name: str
    description: str
    func: Callable
    instruction: Optional[str] = None  # Added instruction field

class Agent:
    def __init__(self, tools: List[Tool], llm_client: OpenRouterClient):
        self.tools = tools
        self.llm_client = OpenRouterClient(api_key=os.getenv('OPENROUTER_API_KEY'))
        self.llm_client.model = "x-ai/grok-3-mini"  # Updated model name
        
    def preprocess_prompt(self, user_input: str) -> str:
        """Preprocess the user input to include a verb and normalize locations."""
        user_input = add_verb_to_prompt(user_input)
        words = user_input.split()
        if len(words) > 1:  # Check if there's a location to normalize
            words[1] = normalize_location(words[1])
        return " ".join(words)

    def _create_prompt(self, user_input: str) -> str:
        # Filter tools to include only the grocery-related and weather-related tools
        selected_tools = [tool for tool in self.tools if tool.name in [
            "get_household_grocery_report", "get_bangalore_weather"
        ]]

        tools_desc = "\n".join([
            f"- {tool.name}: {tool.description} {tool.instruction if tool.instruction else ''}".strip()
            for tool in selected_tools
        ])

        ############### Prompt Template ###############
        prompt = (
            f"You are a helpful AI assistant that can ONLY work with these specific tools:\n\n"
            f"{tools_desc}\n\n"
            f"Carefully analyze the user's request and select the most relevant tool.\n"
            f"- For groceries-related queries (e.g., 'get me groceries report', 'household grocery list'), use the 'get_household_grocery_report' tool.\n"
            f"- For weather-related queries (e.g., 'what is the weather in Bangalore', 'get Bangalore weather'), use the 'get_bangalore_weather' tool.\n\n"
            f"You MUST use one of the above tools to answer. Always include 'action_input' in your response, even if it is empty. If no suitable tool exists, respond with:\n"
            f"{{\"thought\": \"No appropriate tool available for this query\",\n"
            f" \"action\": \"error\",\n"
            f" \"action_input\": \"no_suitable_tool\"}}\n\n"
            f"To use a tool, respond with:\n"
            f"{{\"thought\": \"your reasoning here\",\n"
            f" \"action\": \"tool_name\",\n"
            f" \"action_input\": \"input_for_tool\"}}\n\n"
            f"User request: {user_input}\n"
            f"Which tool would you like to use?"
        )
        ############### End Prompt Template ###############

        # Debugging: Pretty print the generated prompt
        import pprint
        pprint.pprint(prompt)

        return prompt

    def _parse_response(self, response: Any) -> Dict[str, Any]:
        try:
            # Debug: Log the type and value of the response
            print(f"Debug: Type of response: {type(response)}, Value: {response}")

            # Ensure the response is a string before parsing
            if isinstance(response, dict):
                print("Warning: Response is already a dictionary. Skipping parsing.")
                return response  # Return the dictionary as-is
            parsed_response = json.loads(response)
            return parsed_response
        except json.JSONDecodeError:
            print(f"Raw AI Response: {response}")  # Log raw response for debugging
            return {"thought": "Error parsing response", "action": "error", "action_input": "parse_error"}
    
    async def run(self, user_input: str, max_steps: int = 5) -> str:
        step = 0
        while step < max_steps:
            # Get next action from LLM
            prompt = self._create_prompt(user_input)
            response = self.llm_client.send_prompt(prompt, model=self.llm_client.model)

            # Debugging: Log the AI's response
            print(f"AI Response: {response}")

            # Debugging: Log the raw AI response
            print(f"Raw AI Response: {response}")

            try:
                # Debugging: Print the type of the response object
                print(f"Type of response['response']: {type(response['response'])}")

                # Ensure proper parsing of response['response']
                if isinstance(response["response"], str):
                    parsed_response = json.loads(response["response"])
                else:
                    parsed_response = response["response"]

                # Validate parsed response structure
                if not isinstance(parsed_response, dict) or "action" not in parsed_response:
                    raise ValueError("Parsed response is invalid or missing required keys.")

                parsed = self._parse_response(parsed_response)
            except (KeyError, json.JSONDecodeError, ValueError) as e:
                print(f"Error: Failed to parse AI response. Details: {str(e)}")
                return f"Error: Failed to parse AI response. Details: {str(e)}"

            print(f"Parsed Response: {parsed}")  # Log the parsed response for debugging

            # Handle error cases
            if parsed.get("action") == "error":
                if parsed.get("action_input") == "no_suitable_tool":
                    return "I apologize, but I don't have the appropriate tools to answer this question. I can only help with: " + \
                           ", ".join(tool.name for tool in self.tools)
                return "There was an error processing your request."

            # Execute tool if specified
            if "action" in parsed:
                tool_name = parsed["action"]
                tool_input = parsed.get("action_input")  # Use .get() to avoid KeyError

                # Handle 'none' as a valid input
                if tool_input == "none":
                    tool_input = ""  # Replace 'none' with an empty string

                # Assign a default value if 'action_input' is missing or invalid
                if not tool_input:  # Covers both None and empty string
                    print("Warning: 'action_input' is missing or invalid. Using default value.")
                    tool_input = "default_input"  # Replace with an appropriate default value

                # Find and execute the tool
                if tool_input is None:
                    return "Error: Missing 'action_input' in the response."

                tool = next((t for t in self.tools if t.name == tool_name), None)
                if tool is None:
                    return f"Error: Tool '{tool_name}' not found."

                # Check if the tool function is asynchronous
                if asyncio.iscoroutinefunction(tool.func):
                    result = await tool.func(tool_input)
                else:
                    result = tool.func(tool_input)

                # Debugging: Log the type of the result
                print(f"Result type: {type(result)}")
                print(f"Result value: {result}")

                print(f"Tool '{tool_name}' executed successfully.")

                # Ensure result is a string before returning
                if isinstance(result, dict):
                    return json.dumps(result, indent=2)
                return str(result)

            step += 1

        return "Max steps reached without finding an answer."

# Load environment variables from .env file
load_dotenv()

async def post_to_slack(message: str):
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

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()

async def get_bangalore_weather(input: str):
    # Simulated weather data for debugging
    simulated_weather_data = {
        "location": "Bangalore",
        "temperature": "25°C",
        "condition": "Partly Cloudy"
    }
    print("Simulated weather data is being used.")
    return simulated_weather_data

def get_household_grocery_report(input: str):
    # Example grocery data
    grocery_data = {"items": ["Milk", "Eggs", "Bread"]}
    return grocery_data

# Define the 'get_bangalore_weather' tool
get_bangalore_weather_tool = Tool(
    name="get_bangalore_weather",
    description="Fetches the current weather information for Bangalore and posts it to a Slack channel.",
    func=get_bangalore_weather
)

# Define the 'get_household_grocery_report' tool
get_household_grocery_report_tool = Tool(
    name="get_household_grocery_report",
    description="Fetches the household grocery report.",
    func=get_household_grocery_report
)

def add_verb_to_prompt(prompt: str, default_verb: str = "Find") -> str:
    """Ensure the prompt starts with a verb and allow multiple verbs."""
    allowed_verbs = ["find", "get", "pull", "tell", "enlighten", "bataye"]
    words = prompt.strip().split()
    if words[0].lower() not in allowed_verbs:
        return f"{default_verb} {prompt}"
    return prompt

def normalize_location(location: str) -> str:
    """Normalize location names to handle variations for Bangalore."""
    location_variants = {
        "bangalore": "Bangalore",
        "bengalore": "Bangalore",
        "blr": "Bangalore",
        "sbc": "Bangalore City Railway Station",
        "blrcant": "Bangalore Cantonment"
    }
    normalized = location_variants.get(location.lower(), location)
    return normalized
