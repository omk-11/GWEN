from flask import Flask, request, jsonify
from flask_cors import CORS
from coordinator import handle_request
from event_handler import handle_event
import asyncio

app = Flask(__name__)
CORS(app)

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


@app.route('/voice', methods=['POST'])
def voice():  
    data = request.json
    text = data.get("text")

    print("\n Received:", text)

    response = router(text)

    return  response


def router(user_input):
    if 'cap' in user_input.lower():
        handle_event(user_input)

        return 0
    
    else:
        llm_response = loop.run_until_complete(handle_request(user_input))

        return {
            "status": "ok",
            "received": user_input,
            "response": llm_response
        }

def textTest():
    input_text = input("Enter text: ")
    router(input_text)


if __name__ == "__main__":
    mode = 1

    if mode == 1:
        while True:
            textTest()
        exit(0)

    app.run(host="0.0.0.0", port=5000)