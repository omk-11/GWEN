import json
import requests
import os
import datetime
from tools.reminder.reminder import create_event

import pytz
import dateparser


# 🔌 Call local LLM
def call_llm(prompt):
    res = requests.post("http://localhost:11434/api/generate", json={
        "model": "qwen2.5:3b",
        "prompt": prompt,
        "stream": False
    })
    return res.json()["response"]


# 🧠 Extract JSON safely
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


# 🚀 Main handler
def handle_request(user_text):
    print("🧠 Coordinator got:", user_text)

    with open('prompthub/coordinator.json', 'r') as file:
        feeder = json.load(file)

    prompt = f"""{feeder['coordinator-prompt']}
You are currently operating on date {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.
Return ONLY valid JSON.

User input: {user_text}
"""

    llm_output = call_llm(prompt)
    print("🤖 LLM raw:", llm_output)

    parsed = extract_json(llm_output)

    if not parsed:
        return {"error": "Invalid JSON from LLM"}

    return route_intent(parsed)


# 🔀 Router
def route_intent(data):
    intent = data.get("intent")
    print("Intent:", intent)

    if intent == "reminder":
        return handle_reminder(data)

    elif intent == "search":
        return handle_search(data)

    else:
        return {"status": "unknown intent", "data": data}


# ⏰ Reminder handler (FIXED CORE)
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

    # 🔥 FORCE correct timezone (no double conversion)
    parsed_time = parsed_time.astimezone(tz)

    # Ensure timezone-aware
    if parsed_time.tzinfo is None:
        parsed_time = tz.localize(parsed_time)
    else:
        parsed_time = parsed_time.astimezone(tz)

    # Add duration
    end_time = parsed_time + datetime.timedelta(hours=1)
    print("DEBUG:", parsed_time, parsed_time.tzinfo)
    # Send CLEAN ISO format
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


# 🔍 Search handler
def handle_search(data):
    query = data.get("data", {}).get("query")

    print(f"🔍 Searching for: {query}")

    return {
        "status": "search_done",
        "query": query
    }