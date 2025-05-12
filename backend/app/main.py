from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import os

# Initialize Flask app
app = Flask(__name__, static_folder='../../frontend/build')
CORS(app)

# API Route Example
@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify({'message': 'Hello from Flask!'}), 200

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
