from flask import Flask, render_template, request, jsonify
from requests import get
from bs4 import BeautifulSoup
import yaml
import os

app = Flask(__name__)

# Load responses from YAML file
def load_responses():
    try:
        with open('data/responses.yml', 'r') as file:
            responses = yaml.safe_load(file)
            return {key.lower(): value for key, value in responses.items()}  # Ensure keys are lowercase
    except Exception as e:
        print(f"Error loading YAML file: {e}")
        return {}

responses = load_responses()

@app.route("/")
def hello():
    return render_template('chat.html')

@app.route("/ask", methods=['POST'])
def ask():
    message = str(request.form['messageText']).lower()

    # Check for predefined responses in YAML file
    if message in responses:
        bot_response = responses[message]
        return jsonify({'status': 'OK', 'answer': bot_response})

    # If no predefined response, try fetching from Wikipedia
    try:
        url = f"https://en.wikipedia.org/wiki/{message.replace(' ', '_')}"
        page = get(url).text
        soup = BeautifulSoup(page, "html.parser")
        paragraphs = soup.find_all("p")

        # Return the first paragraph with content
        for p in paragraphs:
            if p.text.strip():
                return jsonify({'status': 'OK', 'answer': p.text.strip()})

    except Exception as error:
        print(f"Error fetching from Wikipedia: {error}")

    # Default response if no match is found
    bot_response = 'Sorry, I have no idea about that.'
    return jsonify({'status': 'OK', 'answer': bot_response})

if __name__ == "__main__":
    app.run(debug=True)
