
from flask import Flask, request, jsonify
from flask_cors import CORS
import ollama
from llm.llm import create_message, chat_messages, system_data
from utils.database import execute_sql_query

app = Flask(__name__)
CORS(app)

@app.route('/api/message', methods=['POST'])
def handle_message():
    try:
        # Parse the incoming JSON request
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({"error": "Invalid request"}), 400

        user_message = data['message']

        # Use the ollama module to generate an SQL query
        try:
            global chat_messages

            chat_messages.append({'role': 'user', 'content': user_message})
            r1 = ollama.chat(model='llama3.1', messages=chat_messages)
            sql_query = r1['message']['content']
            print(sql_query)

            # Limit chat_messages to 20 entries
            if len(chat_messages) >= 2:
                chat_messages.pop(0)

        except Exception as e:
            print(f"Error with ollama module: {e}")
            return jsonify({"response": "Error generating SQL query"}), 500

        # Execute the SQL query and fetch results
        query_results = str(execute_sql_query(sql_query))

        chat_messages.append({'role': 'tool', 'content':f"You are an assistant that analyzes a video and gives a response. Respond to the user's question relating to this data: {query_results}."})

        # Generate a response based on the processed data
        try:
            r2 = ollama.chat(model='llama3.1', messages=chat_messages)
            final_response = r2['message']['content']
            chat_messages.append(create_message(final_response, 'assistant'))
            print(chat_messages)
        except Exception as e:
            print(f"Error with ollama module during data processing: {e}")
            return jsonify({"response": "Error processing data"}), 500
        
        chat_messages.clear()
        chat_messages = [{'role': 'user', 'content': system_data}]

        # Return the query results as JSON
        return jsonify({"response": final_response}), 200

    except Exception as e:
        print(f"Error handling message: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
