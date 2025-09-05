import os
import requests
from dotenv import load_dotenv
from typing import Optional, Dict, Any

class OpenRouterClient:
    def __init__(self, api_key: Optional[str] = None):
        # Load environment variables if api_key not provided
        if not api_key:
            load_dotenv(dotenv_path="../.env")
            api_key = os.getenv('OPENROUTER_API_KEY')
        
        if not api_key:
            raise ValueError("API key must be provided or set in environment variables")
        
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1"
    
    def _get_headers(self) -> Dict[str, str]:
        return {
            "HTTP-Referer": "https://github.com/forvaidya",
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def send_prompt(
        self, 
        prompt: str, 
        model: str = "mistralai/mistral-7b-instruct"  # Default to Mistral model
    ) -> Dict[str, Any]:
        try:
            headers = self._get_headers()
            print(f"Using API key: {self.api_key[:8]}...")
            
            payload = {
                "model": model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }

            print("Sending request to OpenRouter...")
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            )
            print(f"Response status code: {response.status_code}")

            if response.status_code == 200:
                response_data = response.json()
                print("Successfully received response")

                # Debug: Log the raw response data
                print(f"Raw response data: {response_data}")

                # Ensure the content is a string
                content = response_data['choices'][0]['message']['content']
                if not isinstance(content, str):
                    raise ValueError("Expected content to be a string, but got: " + str(type(content)))

                return {
                    "status": "success",
                    "response": content,
                    "model_used": response_data.get('model', 'unknown'),
                    "usage": {
                        "prompt_tokens": response_data['usage']['prompt_tokens'],
                        "completion_tokens": response_data['usage']['completion_tokens'],
                        "total_tokens": response_data['usage']['total_tokens']
                    }
                }
            else:
                error_msg = f"Error: {response.status_code}, {response.text}"
                print(f"Request failed: {error_msg}")
                return {
                    "status": "error",
                    "error": error_msg
                }
        except Exception as e:
            error_msg = f"Exception occurred: {str(e)}"
            print(error_msg)
            return {
                "status": "error",
                "error": error_msg
            }

# For standalone usage
if __name__ == "__main__":
    client = OpenRouterClient()
    test_prompt = "What is artificial intelligence?"
    result = client.send_prompt(test_prompt)
    print(f"\nPrompt: {test_prompt}")
    print(f"Response: {result['response'] if result['status'] == 'success' else result['error']}")
