import json

from openai import OpenAI

from agent.prompts import SYSTEM_PROMPT
from agent.tools import get_current_weather
from config import OPENAI_API_KEY, OPENAI_MODEL


class WeatherAgent:
    """A small OpenAI-powered agent that can call a weather tool."""

    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = OPENAI_MODEL
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_current_weather",
                    "description": "Get the current live weather for a city or location.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "The city or location, such as Austin or New York.",
                            }
                        },
                        "required": ["location"],
                        "additionalProperties": False,
                    },
                },
            }
        ]

    def run(self, user_input: str) -> str:
        """Send the user's message to the model and return the final answer."""
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input},
        ]

        first_response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=self.tools,
            tool_choice="auto",
        )

        assistant_message = first_response.choices[0].message

        # If the model does not need a tool, return its answer directly.
        if not assistant_message.tool_calls:
            return assistant_message.content or "I am not sure how to answer that."

        messages.append(assistant_message)

        for tool_call in assistant_message.tool_calls:
            tool_result = self._handle_tool_call(tool_call)
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(tool_result),
                }
            )

        final_response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
        )

        return final_response.choices[0].message.content or "I could not create a weather summary."

    def _handle_tool_call(self, tool_call) -> dict:
        """Run the local Python function requested by the model."""
        function_name = tool_call.function.name

        if function_name != "get_current_weather":
            return {"error": f"Unknown tool requested: {function_name}"}

        try:
            arguments = json.loads(tool_call.function.arguments or "{}")
        except json.JSONDecodeError:
            return {"error": "The model provided invalid tool arguments."}

        location = arguments.get("location")
        return get_current_weather(location)
