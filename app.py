"""
app.py

Flask backend for the Sports Chatbot.
Receives a user message from the frontend, sends it to the Gemini API
along with the sports-only system prompt, and returns the reply as JSON.
"""

import os

from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import google.generativeai as genai

from chatbot_config import SYSTEM_PROMPT

# Load environment variables from .env
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is not set. Please add it to your .env file."
    )

genai.configure(api_key=GEMINI_API_KEY)

# Create the model once with the sports-only system instruction
model = genai.GenerativeModel(
    model_name=MODEL_NAME,
    system_instruction=SYSTEM_PROMPT,
)

app = Flask(__name__)


@app.route("/")
def home():
    """Render the chat UI."""
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    """Receive a user message and return the Gemini model's reply."""
    data = request.get_json(silent=True) or {}
    user_message = (data.get("message") or "").strip()

    if not user_message:
        return jsonify({"error": "No message provided."}), 400

    try:
        response = model.generate_content(user_message)
        reply_text = response.text
    except Exception as exc:  # noqa: BLE001
        return jsonify({"error": f"Something went wrong: {exc}"}), 500

    return jsonify({"reply": reply_text})


if __name__ == "__main__":
    app.run(debug=True)
