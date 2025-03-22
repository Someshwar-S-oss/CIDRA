
from flask import Flask, request, jsonify
from flask_cors import CORS
import ollama

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

system_prompt = "You are an assistant meant to help me fetch data and inform me about the query response. You receive data on vehicles (license plate, colour, type) that pass by a camera and is recorded in a video. I ask you questions about the vehicles that pass and your job is to answer them. Remember you do not have any data on you until i feed it to you. Do not hallucinate."

chat_messages = [{'role': 'system', 'content': system_prompt}]

def create_message(message, role):
    return {
        'role': role,
        'content': message
    }

@app.route('/api/message', methods=['POST'])
def handle_message():
    try:
        # Parse the incoming JSON request
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({"error": "Invalid request"}), 400

        user_message = data['message']

        # Use the ollama module to generate a response
        try:
            global chat_messages
    
            chat_messages.append({'role': 'user', 'content': user_message})
            r1 = ollama.chat(model='llama3.1', messages=chat_messages)
            response = r1['message']['content']

            chat_messages.append(create_message(response, 'assistant'))
            print(chat_messages)

            if len(chat_messages) >= 20:
                chat_messages.pop(1)

        except Exception as e:
            print(f"Error with ollama module: {e}")
            return jsonify({"response": "Error generating response"}), 500

        # Return the bot's response as JSON
        return jsonify({"response": response}), 200

    except Exception as e:
        print(f"Error handling message: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)