from flask import Flask, request, render_template, jsonify, send_from_directory
from groq import Groq
import os
import logging

app = Flask(__name__, template_folder="../templates", static_folder="../static")
logging.basicConfig(level=logging.DEBUG)

# System prompt for AI psychologist
SYSTEM_PROMPT = """
You are a compassionate AI psychologist. Provide empathetic, supportive, and non-judgmental responses. 
Always prioritize user well-being, avoid giving medical diagnoses, and suggest professional help for serious issues. 
If the user expresses a crisis (e.g., suicidal thoughts), respond with: 
'I'm here for you, but it sounds like you might need immediate support. Please contact a trusted professional or a hotline like 988 (in the US) or a local crisis line.'
"""

# Initialize Groq client
try:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set")
    client = Groq(api_key=api_key, http_client=None)
except Exception as e:
    app.logger.error(f"Failed to initialize Groq client: {str(e)}")
    client = None

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/favicon.ico")
@app.route("/favicon.png")
def favicon():
    return send_from_directory(os.path.join(app.root_path, "../static"), "favicon.ico", mimetype="image/vnd.microsoft.icon")

@app.route("/chat", methods=["POST"])
def chat():
    app.logger.debug("Received chat request")
    if not client:
        app.logger.error("Groq client not initialized")
        return jsonify({"error": "AI service unavailable"}), 503

    user_message = request.json.get("message")
    app.logger.debug(f"User message: {user_message}")
    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    # Check for crisis keywords
    crisis_keywords = ["suicide", "kill myself", "end my life", "hopeless"]
    if any(keyword in user_message.lower() for keyword in crisis_keywords):
        return jsonify({
            "response": "I'm here for you, but it sounds like you might need immediate support. Please contact a trusted professional or a hotline like 988 (in the US) or a local crisis line."
        })

    try:
        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=500
        )
        return jsonify({"response": response.choices[0].message.content})
    except Exception as e:
        app.logger.error(f"Groq API error: {str(e)}")
        return jsonify({"error": "Failed to connect to AI service. Please try again later."}), 500

if __name__ == "__main__":
    app.run(debug=os.getenv("VERCEL") is None)
