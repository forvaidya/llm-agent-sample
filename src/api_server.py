from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List

from api_client import OpenRouterClient
from agent import Agent, Tool
from tools import TOOLS

app = FastAPI()

# Initialize OpenRouter client
client = OpenRouterClient()

# Initialize agent with tools
agent = Agent(
    tools=[Tool(name=tool["name"], description=tool["description"], func=tool["func"]) for tool in TOOLS],
    llm_client=client
)

class Prompt(BaseModel):
    text: str
    model: Optional[str] = "mistralai/mistral-7b-instruct"  # Default to Mistral model

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "service": "OpenRouter API Agent",
        "available_tools": [tool["name"] for tool in TOOLS]
    }

@app.post("/ask")
async def ask_question(prompt: Prompt):
    try:
        # Use the agent to process the request
        response = await agent.run(prompt.text)  # Add await here
        return {
            "prompt": prompt.text,
            "response": response,
            "agent": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
