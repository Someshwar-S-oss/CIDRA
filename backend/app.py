
from flask import Flask, request, jsonify
from flask_cors import CORS
import ollama
import os
from llm.llm import create_message, chat_messages, system_data
from utils.database import execute_sql_query, clear_chat, database_operations

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
    

@app.route('/api/clear', methods=['POST'])
def clear():
    return clear_chat()
    

# @app.route('/api/monitor', methods=['GET'])
# def monitor_progress():
#     def generate():
#         try:
#             for progress in start_monitoring():
#                 yield f"data: {progress}\n\n"  # Server-Sent Events (SSE) format
#         except Exception as e:
#             yield f"data: Error: {str(e)}\n\n"

#     return Response(generate(), content_type='text/event-stream')
    
@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    try:
        # Ensure UPLOAD_FOLDER is configured
        app.config['UPLOAD_FOLDER'] = 'uploads'
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])

        # Save the file to the upload folder
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], "video.mp4")
        file.save(file_path)
        print("File saved to:", file_path)

        # Send the video file for processing
        try:
            print("Processing video...")
            result = process_video(file_path)
            print("Video processed. Result:", result)
        except Exception as e:
            print(f"Error processing video: {e}")
            return jsonify({"error": f"Error processing video: {str(e)}"}), 500

        # Process database operations
        try:
            print("Processing database operations...")
            database_operations("./ocr_results_with_timestamps.csv")
            print("Database operations completed.")
        except Exception as e:
            print(f"Error processing database operations: {e}")
            return jsonify({"error": f"Error processing database operations: {str(e)}"}), 500

        return jsonify({"message": "File uploaded successfully", "file_path": os.path.basename(file_path)}), 200
    except Exception as e:
        print(f"Error uploading file: {e}")
        return jsonify({"error": f"Failed to upload file: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
