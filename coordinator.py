import json
import requests
import datetime
import asyncio

from tools.reminder.reminder import create_event
from tools.telegram.sendMessage import send_telegram_message

import pytz
import dateparser


# ---------------- LLM ---------------- #

def call_llm(prompt):
    res = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "qwen2.5:3b",
            "prompt": prompt,
            "stream": False
        }
    )
    return res.json()["response"]


def extract_json(text):
    try:
        return json.loads(text)
    except:
        start = text.find("{")
        end = text.rfind("}") + 1

        if start != -1 and end != -1:
            try:
                return json.loads(text[start:end])
            except:
                pass

    return None


# ---------------- MAIN ENTRY ---------------- #

async def handle_request(user_text):
    print("🧠 Coordinator got:", user_text)

    with open('prompthub/coordinator.json', 'r') as file:
        feeder = json.load(file)

    prompt = f"""{feeder['coordinator-prompt']}
You are currently operating on date {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.
Return ONLY valid JSON.

User input: {user_text}
"""

    llm_output = call_llm(prompt)
    print("LLM raw:", llm_output)

    parsed = extract_json(llm_output)

    if not parsed:
        return {"error": "Invalid JSON from LLM "}

    return await route_intent(parsed)


# ---------------- ROUTER ---------------- #

async def route_intent(data):
    intent = data.get("intent")
    print("🎯 Intent:", intent)

    TOOL_MAP = {
        "reminder": handle_reminder,   # sync
        "text": send_telegram_text,    # async
    }

    func = TOOL_MAP.get(intent)

    if not func:
        return {"status": "unknown intent", "data": data}

    if asyncio.iscoroutinefunction(func):
        return await func(data)
    else:
        return func(data)


# ---------------- TOOLS ---------------- #

def handle_reminder(data):
    task = data.get("data")
    time_str = data.get("date")

    print(f"⏰ Reminder: {task} at {time_str}")

    tz = pytz.timezone("Asia/Kolkata")

    parsed_time = dateparser.parse(
        time_str,
        settings={
            'TIMEZONE': 'Asia/Kolkata',
            'RETURN_AS_TIMEZONE_AWARE': True
        }
    )

    if not parsed_time:
        return {"error": f"Could not parse date: {time_str}"}

    parsed_time = parsed_time.astimezone(tz)

    if parsed_time.tzinfo is None:
        parsed_time = tz.localize(parsed_time)

    end_time = parsed_time + datetime.timedelta(hours=1)

    create_event(
        task,
        parsed_time.isoformat(),
        end_time.isoformat()
    )

    return {
        "status": "reminder_set",
        "task": task,
        "time": parsed_time.isoformat()
    }


async def send_telegram_text(data):
    msg = data.get("data", "Hello from GWEN!")
    target = data.get("target", "tacs_86")

    return await send_telegram_message(msg, target)