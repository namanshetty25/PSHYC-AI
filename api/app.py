from flask import Flask, request, render_template, jsonify
from groq import Groq
import os

app = Flask(__name__, template_folder="../templates", static_folder="../static")
client = Groq(api_key=os.getenv("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"))

# System prompt for AI psychologist
SYSTEM_PROMPT = """
You are a compassionate AI psychologist. Provide empathetic, supportive, and non-judgmental responses. 
Always prioritize user well-being, avoid giving medical diagnoses, and suggest professional help for serious issues. 
If the user expresses a crisis (e.g., suicidal thoughts), respond with: 
'I'm here for you, but it sounds like you might need immediate support. Please contact a trusted professional or a hotline like 988 (in the US) or a local crisis line.'
"""

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")
    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    # Check for crisis keywords
    crisis_keywords = ["suicide", "kill myself", "end my life", "hopeless"]
    if any(keyword in user_message.lower() for keyword in crisis_keywords):
        return jsonify({
            "response": "I'm here for you, but it sounds like you might need immediate support. Please contact a trusted professional or a hotline like 988 (in the US) or a local crisis line."
        })

    try:
        # Call Groq API with Mistral model
        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",  # Mistral model
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,  # Balanced tone
            max_tokens=500
        )
        return jsonify({"response": response.choices[0].message.content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=os.getenv("VERCEL") is None)