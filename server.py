from flask import Flask, request, jsonify
from flask_cors import CORS
from coordinator import handle_request
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

    # ✅ RUN async function properly
    llm_response = loop.run_until_complete(handle_request(text))

    return jsonify({
        "status": "ok",
        "received": text,
        "response": llm_response
    })


def textTest():
    input_text = input("Enter text: ")
    llm_output = loop.run_until_complete(handle_request(input_text))

    print("LLM Output:", llm_output)


if __name__ == "__main__":
    mode = 0

    if mode == 1:
        textTest()
        exit(0)

    app.run(host="0.0.0.0", port=5000)