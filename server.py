from flask import Flask, request, jsonify
from flask_cors import CORS
from coordinator import handle_request

app = Flask(__name__)
CORS(app)

@app.route('/voice', methods=['POST'])
def voice():
    data = request.json
    text = data.get("text")

    print("\n Received:", text)

    llm_response = handle_request(text)

    response = {
        "status": "ok",
        "received": text
    }

    return jsonify(response)

def textTest():
    # 🔹 Step 1: Create prompt
    input_text = input("Enter text: ")
    llm_output = handle_request(input_text)
    print("LLM Output:", llm_output)

if __name__ == "__main__":
    mode = 1
    if mode == 1:
        textTest()
        exit(0)
    app.run(host="0.0.0.0", port=5000)

