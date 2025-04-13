from dotenv import load_dotenv
import os
from openai import OpenAI
import json
import requests

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAPI_KEY"),
)


def get_weather(city: str) -> str:
    print("🔨 Tool Called: get_weather", city)
    url = f"https://wttr.in/{city}?format=%C+%t"
    response = requests.get(url)

    if response.status_code == 200:
        return f"The weather in {city} is {response.text}."
    return "Something went wrong"


system_prompt = f"""
    You are an helpfull AI Assistant who is specialized in resolving user query.
    You work on start, plan, action, observe mode.
    For the given user query and available tools, plan the step by step execution, based on the planning,
    select the relevant tool from the available tool. and based on the tool selection you perform an action to call the tool.
    Wait for the observation and based on the observation from the tool call resolve the user query.

    Rules:
    - Follow the Output JSON Format.
    - Always perform one step at a time and wait for next input
    - Carefully analyse the user query

    Output JSON Format:
    {{
        "step": "string",
        "content": "string",
        "function": "The name of function if the step is action",
        "input": "The input parameter for the function",
    }}
    
    Available Tools:
    - get_weather: Takes a city name as an input and returns the current weather for the city
    
    Example:
    User Query: What is the weather of new york, united states?
    Output: {{ "step": "plan", "content": "The user is interseted in weather data of new york" }}
    Output: {{ "step": "plan", "content": "From the user input the city is new york" }}
    Output: {{ "step": "plan", "content": "From the available tools I should call get_weather" }}
    Output: {{ "step": "action", "function": "get_weather", "input": "new york" }}
    Output: {{ "step": "observe", "output": "12 Degree Cel" }}
    Output: {{ "step": "output", "content": "The weather for new york seems to be 12 degrees." }}
"""


avialable_tools = {
    "get_weather": {
        "description": "Takes a city name as an input and returns the current weather for the city",
        "fn": get_weather,
    }
}


while True:
    messages = [
        {"role": "system", "content": system_prompt},
    ]

    user_query = input("➡️➡️ Enter your query: ")
    messages.append({"role": "user", "content": user_query})
    if user_query.lower() == "exit":
        print("Exiting...")
        break
    while True:
        response = client.chat.completions.create(
            model="gpt-4o", response_format={"type": "json_object"}, messages=messages
        )

        parsed_response = json.loads(response.choices[0].message.content)
        messages.append(response.choices[0].message)

        if parsed_response["step"] == "output":
            print(parsed_response["content"])
            break

        elif parsed_response["step"] == "action":
            if avialable_tools.get(parsed_response["function"]):
                function = avialable_tools[parsed_response["function"]]["fn"]
                input_param = parsed_response["input"]
                output = function(input_param)
                messages.append(
                    {
                        "role": "assistant",
                        "content": json.dumps(
                            {
                                "step": "observe",
                                "output": output,
                            }
                        ),
                    }
                )
            else:
                print("Function not found.")
                break
        elif parsed_response["step"] == "plan":
            print(parsed_response["content"])
            messages.append(
                {
                    "role": "assistant",
                    "content": json.dumps(
                        {
                            "step": "plan",
                            "content": parsed_response["content"],
                        }
                    ),
                }
            )
        else:
            print("Invalid step.")
            break
