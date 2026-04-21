import json
import requests
import os
from tools.reminder.reminder import create_event

# 🔥 Replace with your LLM (Ollama example)
def call_llm(prompt):
    res = requests.post("http://localhost:11434/api/generate", json={
        "model": "llama3.1:8b",
        "prompt": prompt,
        "stream": False
    })

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

def handle_request(user_text):
    print("🧠 Coordinator got:", user_text)

    with open('prompthub/coordinator.json','r') as file:
        feeder = json.load(file)
    # feeder prompt 
    prompt = f"{feeder['coordinator-prompt']} {user_text}"

    # Step 2: Call LLM
    llm_output = call_llm(prompt)

    print("🤖 LLM raw:", llm_output)

    # Step 3: Parse JSON
    parsed = extract_json(llm_output)

    if not parsed:
        return {"error": "Invalid JSON from LLM"}

    # Step 4: Route intent
    return route_intent(parsed)


#  Intent router
def route_intent(data):
    intent = data.get("intent")
    print(" Intent:", intent)

    if intent == "reminder":
        return handle_reminder(data)

    elif intent == "search":
        return handle_search(data)

    else:
        return {"status": "unknown intent", "data": data}


# 🔧 Example handlers
def handle_reminder(data):
    task = data.get("data")
    time = data.get("date")

    print(f"⏰ Reminder: {task} at {time}")
    create_event(task, time, time)

    return {
        "status": "reminder_set",
        "task": task,
        "time": time
    }


def handle_search(data):
    query = data.get("data", {}).get("query")

    print(f"🔍 Searching for: {query}")

    return {
        "status": "search_done",
        "query": query
    }