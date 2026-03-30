import os
import requests
import json
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi import FastAPI
import random

load_dotenv()

api_key = os.getenv("API_KEY")

if not api_key:
    raise ValueError("API Key is missing in .env file")

app = FastAPI()
memory = {}

class Message(BaseModel):
    session_id : str
    message : str

restaurant = {
    "name": "Bella Italia",
    "opening_hours": "12 PM to 11 PM",
    "location" : "Astoria",
    "total_tables": 10,
    "max_per_table": 8,
    "menu": {
        "pizzas": ["Margherita", "Pepperoni", "Vegetarian", "Spicy Chicken"],
        "pastas": ["Carbonara", "Bolognese", "Vegan Arrabbiata"],
        "desserts": ["Tiramisu", "Gelato", "Panna Cotta"]
    },
    "dietary_options": ["vegetarian", "vegan", "gluten_free"],
    "reservations": []
}


def check_availability(date, time, people):
    if restaurant["total_tables"] <= 0:
        return "Sorry, all tables have already been booked"
    if int(people) > 8:
        return "Sorry, we only serve maximum 8 people per table"
    return "Tables are available"

def check_menu(category=None):
    if category is None:
        result = "Our full Menu:\n"
        for cat, items in restaurant["menu"].items():
            result += f"\n{cat.upper()} : {','.join(items)}"
        return result
    category = category.lower()
    if category in restaurant["menu"]:
        items = restaurant["menu"][category]
        return f"{category.upper()} : {','.join(items)}"

    return f"Category : '{category}' not found. Available: pizzas, pastas, desserts"


def check_dietary_options(requirement):
    requirement = requirement.lower()
    if requirement not in restaurant["dietary_options"]:
        return f"Sorry, {requirement} option is not available"
    return f"yes we have {requirement} option available!"

def book_table(date, time, people, special_requirement=None):
    ref = random.randint(1000,9999)
    reservation = {
        "ref" : ref,
        "date" : date,
        "time" : time,
        "people" : people,
        "special_requirement" : special_requirement
    }
    restaurant["reservations"].append(reservation)
    restaurant["total_tables"] -= 1
    
    return f"Table booked! Reference number : {ref}. Date: {date}, Time: {time}, People: {people}."

def get_restaurant_info():
    name = restaurant["name"]
    hours = restaurant["opening_hours"]
    location = restaurant["location"]
    return f"Name: {name}\nOpening hours: {hours}\nLocation: {location}"

tools = [
    {
        "type": "function",
        "function": {
            "name": "check_availability",
            "description": "Checks if a table is available",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "Date given by customer, on which they are going to have dinner"
                    },
                    "time": {
                        "type": "string",
                        "description": "Time given by customer, in which they are going to have dinner"
                    },
                    "people": {
                        "type": "integer",
                        "description": "Number of people e.g. 5"
                    }
                },
                "required": ["date", "time", "people"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "check_menu",
            "description": "return full menu or specific category",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Categories of food e.g. pizzas"
                    }
                },
                "required": []
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "check_dietary_options",
            "description": "Checks if specific dietary requirement is available",
            "parameters": {
                "type": "object",
                "properties": {
                    "requirement": {
                        "type": "string",
                        "description": "requirements like vegetarian, vegan etc.."
                    }
                },
                "required": ["requirement"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "book_table",
            "description": "Books a table",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "Date given by customer, on which they are going to have dinner"
                    },
                    "time": {
                        "type": "string",
                        "description": "Time given by customer, in which they are going to have dinner"
                    },
                    "people": {
                        "type": "integer",
                        "description": "Number of people e.g. 5"
                    },
                    "special_requirement": {
                        "type": "string",
                        "description": "requirements like vegetarian, vegan etc.."
                    }

                },
                "required": ["date", "time", "people"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "get_restaurant_info",
            "description": "Returns restaurant name, hours, location",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]


def system_prompt():
    return f"""
    You are Naina, a smart booking assistant for Bella Italia restaurant.
    Your goal is to help customers make reservations, and answer questions.

    For every booking request follow these steps:
    1. UNDERSTAND - Identify what the customer needs
    2. GATHER - collect all the information:
        - date and time
        - number of people
        - any dietary requirements
    3. VALIDATE - check availability and menu
    4. EXECUTE - make the booking
    5. CONFIRM - give complete confirmation.

    Before acting always ask youself:
    - DO i have all required information?
    - Is the customer's request possible?
    - what is the correct order of steps?
    - What tools do I need?

    Never book a table without:
    - Date and time
    - Number of people
    If either is missing, ask for it first.

    Always be warm, friendly, and professional.
    Keep response concise and clear.
    Only answer questions related to Bella Italia.
    If asked anything unrelated politely, redirect.

    Always respond in JSON:
    {{
        "step": "understand/gather/validate/execute/confirm",
        "message": "your response here",
        "action_taken": "what you did or null",
        "missing_info": ["list of missing info or empty"]
    }}
"""

def ask_ai(chat_history):
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json = {
                "model": "llama-3.3-70b-versatile",
                "temperature" : 0.3,
                "max_tokens" : 500,
                "messages" : [
                    {"role" : "system", "content" : system_prompt()},
                    *chat_history
                ],
                "tools" : tools,
                "tool_choice" : "auto"
            },
            timeout=10
        )
        response.raise_for_status()
        message = response.json()["choices"][0]["message"]

        if message.get("tools_calls"):
            tool_call = message["tool_call"][0]
            function_name = tool_call["function"]["name"]
            arguments = json.loads(tool_call["function"]["argumenets"])

            if function_name == "check_availability":
                arguments["people"] = int(arguments["people"])
                result = check_availability(**arguments)
            elif function_name == "check_menu":
                result == check_menu(**arguments)
            elif function_name == "check_dietary_options":
                result = check_dietary_options(**arguments)
            elif function_name == "book_table":
                arguments["people"] = int(arguments["people"])
                result = book_table(**arguments)
            elif function_name == "get_restaurant_info":
                result = get_restaurant_info()
            else:
                result = "Function not found"
            
            chat_history.append(message)
            chat_history.append({
                "role" : "tool",
                "tool_call_id" : tool_call["id"],
                "content" : result
            })
            
            final_response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json = {
                    "model": "llama-3.3-70b-versatile",
                    "temperature" : 0.3,
                    "max_tokens" : 500,
                    "messages" : [
                        {"role" : "system", "content" : system_prompt()},
                        *chat_history
                    ],
                    "tools" : tools,
                    "tool_choice" : "auto"
                },
                timeout=10
            )

            final_response.raise_for_status()
            raw = final_response.json()["choices"][0]["message"]["content"]
            return {"reply": json.loads(raw)}
        content = message["content"]
        try:
            return {"reply" : json.loads(content)}
        except json.JSONDecodeError:
            return {"reply" : content}
    except requests.exceptions.Timeout:
        return "Time out! Please try again."
    except requests.exceptions.ConnectionError:
        return "Connection Error! Please check your network."
    except requests.exceptions.HTTPError as e:
        return f"API Error {e.response.status_code}"
    except Exception as e:
        return f"Something went wrong! {str(e)}"
    

@app.post("/book")
def booking_ai(message: Message):
    if not message.session_id:
        return "Session ID is missing"
    if not message.message:
        return "Please type something before sending"
    
    session_id = message.session_id
    user_message = message.message

    if session_id not in memory:
        memory[session_id] = []

    memory[session_id].append({"role" : "user", "content": user_message})
    ai_reply = ask_ai(memory[session_id])

    if isinstance(ai_reply, dict) and "reply" in ai_reply:
        memory[session_id].append({"role" : "assistant", "content" : json.dumps(ai_reply["reply"])})
    return ai_reply
