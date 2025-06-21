from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
from dotenv import load_dotenv
from .db import db_client

# Load environment variables
load_dotenv()

# Initialize Flask app
static_folder_path = os.getenv('STATIC_FOLDER', os.path.abspath(os.path.join(os.path.dirname(__file__), '../../frontend/build')))
app = Flask(__name__, static_folder=static_folder_path)
CORS(app)

# Example API Route to Add Data to DynamoDB
@app.route('/api/add', methods=['POST'])
def add_data():
    data = request.json
    table_name = os.getenv('DYNAMODB_TABLE_NAME', 'TestTable1')
    try:
        response = db_client.put_item(table_name=table_name, item=data)
        return jsonify({'message': 'Data added successfully!', 'response': response}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Example API Route to Fetch Data from DynamoDB
@app.route('/api/data', methods=['GET'])
def get_data():
    table_name = os.getenv('DYNAMODB_TABLE_NAME', 'TestTable1')
    try:
        items = db_client.scan(table_name=table_name)
        return jsonify(items), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Serve React Static Files
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react_app(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

# Run Flask App
if __name__ == '__main__':
    app.run(debug=True)
