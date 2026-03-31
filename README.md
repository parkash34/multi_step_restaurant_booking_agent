# SmartBooking — Multi-Step Restaurant Booking Agent

A smart AI booking agent for Bella Italia restaurant built with FastAPI
and Groq AI. The agent uses multi-step reasoning to handle complex booking
requests, proactively gathering missing information before executing actions.

## Features

- Multi-step reasoning — agent thinks before acting
- Task decomposition — breaks complex requests into 5 structured steps
- Proactive information gathering — asks for missing details automatically
- Table booking with reference number generation
- Menu checking — full menu or specific category
- Dietary options checking — vegetarian, vegan, gluten free
- Restaurant information — hours, location, details
- Structured JSON responses — step tracking in every reply
- Multi-session memory — each customer has separate conversation history
- Comprehensive error handling

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| FastAPI | Backend web framework |
| Groq API | AI language model provider |
| LLaMA 3.3 70B | AI model |
| Pydantic | Data validation |
| python-dotenv | Environment variable management |

## Project Structure
```
smartbooking/
│
├── .venv/               
├── main.py            
├── .env               
└── requirements.txt   
```

## Setup

1. Clone the repository
```
git clone https://github.com/yourusername/smartbooking
```

2. Create and activate virtual environment
```
python -m venv .venv
.venv\Scripts\activate
```

3. Install dependencies
```
pip install -r requirements.txt
```

4. Create `.env` file and add your Groq API key
```
API_KEY=your_groq_api_key_here
```

5. Run the server
```
uvicorn main:app --reload
```

## API Endpoint

### POST /book

**Request:**
```json
{
    "session_id": "user_1",
    "message": "I want to book a table for 4 tonight at 7 PM"
}
```

**Response:**
```json
{
    "reply": {
        "step": "confirm",
        "message": "Table booked for 4 people tonight at 7 PM. Reference number: 3257",
        "action_taken": "booked table",
        "missing_info": []
    }
}
```

## Agent Reasoning Steps

| Step | What Happens |
|---|---|
| `understand` | Agent identifies what customer needs |
| `gather` | Agent collects missing information |
| `validate` | Agent checks availability and menu |
| `execute` | Agent performs the booking action |
| `confirm` | Agent gives complete confirmation |

## Available Tools

| Tool | Description | Parameters |
|---|---|---|
| `check_availability` | Checks table availability | `date`, `time`, `people` |
| `check_menu` | Returns menu items | `category` (optional) |
| `check_dietary_options` | Checks dietary requirements | `requirement` |
| `book_table` | Books a table | `date`, `time`, `people`, `special_requirement` |
| `get_restaurant_info` | Returns restaurant details | None |

## How It Works
```
User sends message
↓
Agent reasons through the request
↓
Identifies missing information
↓
Asks for missing details if needed
↓
Validates availability and requirements
↓
Executes booking action
↓
Returns structured confirmation
```

## Restaurant Details
```
Name:          Bella Italia
Location:      Astoria
Opening Hours: 12 PM to 11 PM
Max per table: 8 people
Total tables:  10
```

## Booking Rules

- Maximum 8 people per table
- Date and time required before booking
- Special dietary requirements noted on reservation

## Environment Variables
```
API_KEY=your_groq_api_key_here
```

## Notes

- Never commit your .env file to GitHub
- Reservations reset when server restarts
- Agent only answers Bella Italia related questions
```

