from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv # TODO: Set up loading of environment variables from .env file

# Initialize Flask app
app = Flask(__name__, static_folder='../../frontend/build')
CORS(app)

# Sample Initialization of DynamoDB (TODO: set up still in progress)
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')  # TODO: Replace with dynamic region configuration later. Apply us-east-1 for now solely during in dev.
table_name = 'YourTableName'

# Example API Route to Add Data to DynamoDB
@app.route('/api/add', methods=['POST'])
def add_data():
    data = request.json
    table = dynamodb.Table(table_name)
    try:
        table.put_item(Item=data)
        return jsonify({'message': 'Data added successfully!'}), 200
    except ClientError as e:
        return jsonify({'error': str(e)}), 500

# Example API Route to Fetch Data from DynamoDB
@app.route('/api/data', methods=['GET'])
def get_data():
    table = dynamodb.Table(table_name)
    try:
        response = table.scan()
        return jsonify(response['Items']), 200
    except ClientError as e:
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
