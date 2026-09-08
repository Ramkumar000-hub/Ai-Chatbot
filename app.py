"""
AI Chatbot & Image Generation Web App
--------------------------------------
Flask backend that powers:
  1. Conversational chat via the Groq API
  2. Text-to-image generation via the Stability AI API

Author: Ram Kumar
"""

import os
import base64
import threading
import webbrowser
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
load_dotenv()  # Loads variables from a local .env file

# --- Temporary debug lines: confirm whether the .env file was found ---
print("Looking for .env in:", os.getcwd())
print("GROQ_API_KEY loaded:", "YES" if os.getenv("GROQ_API_KEY") else "NO")
print("STABILITY_API_KEY loaded:", "YES" if os.getenv("STABILITY_API_KEY") else "NO")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")

GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "openai/gpt-oss-20b"  # swap for any model available on your Groq account

STABILITY_URL = "https://api.stability.ai/v2beta/stable-image/generate/core"

app = Flask(__name__)

# In-memory conversation store (per server run — not persisted).
# For multi-user or production use, replace with a proper session/DB store.
conversation_history = []


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    """Render the main chat + image generation UI."""
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    """Send the user's message to Groq and return the assistant's reply."""
    if not GROQ_API_KEY:
        return jsonify({"error": "GROQ_API_KEY is not set. Add it to your .env file."}), 500

    data = request.get_json(silent=True) or {}
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"error": "Message cannot be empty."}), 400

    conversation_history.append({"role": "user", "content": user_message})

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": conversation_history,
        "temperature": 0.7,
        "max_tokens": 1024,
    }

    try:
        response = requests.post(GROQ_CHAT_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        reply = result["choices"][0]["message"]["content"]

        conversation_history.append({"role": "assistant", "content": reply})

        return jsonify({"reply": reply})

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Groq API request failed: {str(e)}"}), 502
    except (KeyError, IndexError):
        return jsonify({"error": "Unexpected response format from Groq API."}), 502


@app.route("/api/generate-image", methods=["POST"])
def generate_image():
    """Send a text prompt to Stability AI and return a base64-encoded image."""
    if not STABILITY_API_KEY:
        return jsonify({"error": "STABILITY_API_KEY is not set. Add it to your .env file."}), 500

    data = request.get_json(silent=True) or {}
    prompt = data.get("prompt", "").strip()

    if not prompt:
        return jsonify({"error": "Prompt cannot be empty."}), 400

    headers = {
        "Authorization": f"Bearer {STABILITY_API_KEY}",
        "Accept": "image/*",
    }
    files = {"none": ""}  # Stability's v2beta endpoint expects multipart/form-data
    data_payload = {
        "prompt": prompt,
        "output_format": "png",
    }

    try:
        response = requests.post(
            STABILITY_URL,
            headers=headers,
            files=files,
            data=data_payload,
            timeout=60,
        )
        response.raise_for_status()

        image_base64 = base64.b64encode(response.content).decode("utf-8")
        return jsonify({"image": f"data:image/png;base64,{image_base64}"})

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Stability AI request failed: {str(e)}"}), 502


@app.route("/api/reset", methods=["POST"])
def reset_conversation():
    """Clear the in-memory chat history."""
    conversation_history.clear()
    return jsonify({"status": "conversation reset"})


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
APP_URL = "http://127.0.0.1:5000"


def open_browser():
    """Open the app in Chrome once the server is ready. Falls back to the
    system default browser if Chrome isn't found."""
    try:
        chrome_path = None
        possible_paths = [
            "C:/Program Files/Google/Chrome/Application/chrome.exe",
            "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
        ]
        for path in possible_paths:
            if os.path.exists(path):
                chrome_path = path
                break

        if chrome_path:
            webbrowser.get(f'"{chrome_path}" %s').open(APP_URL)
        else:
            webbrowser.open(APP_URL)
    except webbrowser.Error:
        print(f"Could not open a browser automatically. Visit {APP_URL} manually.")


if __name__ == "__main__":
    # Only open the browser in the main process (avoids double-opening
    # when Flask's debug reloader spawns a child process).
    if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        threading.Timer(1.0, open_browser).start()

    app.run(debug=True)