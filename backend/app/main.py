from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
from dotenv import load_dotenv
from .db import db_client
from .embeddings import store_habit_embedding, get_habit_embedding
from .ml_models import HabitFrequencyKNN, HabitPredictor
import openai
import uuid
from datetime import datetime
from .config.db_config import get_db_config
from .ml_concurrent import concurrent_predict_habits

# Load environment variables
load_dotenv()

# Initialize Flask app
static_folder_path = os.getenv('STATIC_FOLDER', os.path.abspath(os.path.join(os.path.dirname(__file__), '../../frontend/build')))
app = Flask(__name__, static_folder=static_folder_path)
CORS(app)

# Serve React Static Files
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react_app(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/habit/embedding', methods=['POST'])
def add_habit_embedding():
    data = request.json
    user_id = data['user_id']
    habit_id = data['habit_id']
    text = data['text']
    try:
        item = store_habit_embedding(user_id, habit_id, text, 'Habits')
        return jsonify({'message': 'Embedding stored!', 'item': item}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/habit/predict', methods=['GET'])
def predict_habit():
    user_id = request.args.get('user_id')
    habit_id = request.args.get('habit_id')
    try:
        # Query HabitLogs for this user and habit
        # SK format: HABIT#<HabitID>#
        prefix = f"HABIT#{habit_id}#"
        logs = db_client.scan(
            'HabitLogs',
            filter_expression='UserID = :uid AND begins_with(SK, :prefix)',
            expression_attribute_values={':uid': user_id, ':prefix': prefix}
        )
        if not logs:
            return jsonify({'error': 'No logs found for user/habit'}), 404
        model = HabitFrequencyKNN()
        model.fit(logs)
        predictions = model.predict(logs)
        return jsonify({'predictions': predictions}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/habit/prediction', methods=['POST'])
def store_habit_prediction():
    data = request.json
    user_id = data['user_id']
    habit_id = data['habit_id']
    prediction_id = data['prediction_id']
    generated_at = data['generated_at']
    prediction_type = data['prediction_type']
    prediction_value = data['prediction_value']
    model_id = data.get('model_id', '')
    confidence = data.get('confidence', 1.0)
    item = {
        'UserID': user_id,
        'SK': f'{habit_id}#{generated_at}#{prediction_id}',
        'HabitID': habit_id,
        'GeneratedAt': generated_at,
        'PredictionType': prediction_type,
        'PredictionValue': prediction_value,
        'ModelID': model_id,
        'Confidence': confidence
    }
    try:
        db_client.put_item('HabitPredictions', item)
        return jsonify({'message': 'Prediction stored!', 'item': item}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_openai_client():
    api_key = get_db_config().openai_api_key
    return openai.OpenAI(api_key=api_key)

@app.route('/api/habit/external_feedback', methods=['POST'])
def generate_external_feedback():
    data = request.json
    user_id = data['user_id']
    habit_id = data['habit_id']
    habit_text = data['habit_text']
    feedback_type = data.get('feedback_type', 'habit-improvement')
    source = 'OpenAI'
    feedback_id = str(uuid.uuid4())
    fetched_at = datetime.utcnow().isoformat() + 'Z'
    # Call OpenAI to generate feedback
    try:
        client = get_openai_client()
        prompt = f"Provide actionable feedback or advice to improve the following habit: '{habit_text}'"
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "You are a helpful habit improvement assistant."},
                      {"role": "user", "content": prompt}]
        )
        content = response.choices[0].message.content.strip()
        item = {
            'UserID': user_id,
            'FeedbackID': feedback_id,
            'Source': source,
            'FetchedAt': fetched_at,
            'Content': content,
            'FeedbackType': feedback_type,
            'RelatedHabitID': habit_id,
            'ProviderMetadata': {},
            'Processed': False,
            'ExpiresAt': None
        }
        db_client.put_item('ExternalFeedback', item)
        return jsonify({'message': 'Feedback generated and stored!', 'item': item}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/habit/feedback_action', methods=['POST'])
def record_feedback_action():
    data = request.json
    user_id = data['user_id']
    feedback_id = data['feedback_id']
    action_type = data['action_type']
    action_id = str(uuid.uuid4())
    action_at = datetime.utcnow().isoformat() + 'Z'
    comment = data.get('comment', None)
    metadata = data.get('metadata', {})
    # SK: FeedbackID#ActionAt#ActionID
    sk = f'{feedback_id}#{action_at}#{action_id}'
    item = {
        'UserID': user_id,
        'SK': sk,
        'FeedbackID': feedback_id,
        'ActionType': action_type,
        'ActionAt': action_at,
        'ActionID': action_id,
        'Comment': comment,
        'Metadata': metadata
    }
    try:
        db_client.put_item('FeedbackActions', item)
        return jsonify({'message': 'Feedback action recorded!', 'item': item}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/habit/predictions/generate', methods=['POST'])
def generate_habit_predictions():
    data = request.json
    user_id = data['user_id']
    model_id = data.get('model_id', 'default-rl')
    habits = db_client.get_habits_for_user(user_id)
    # Use concurrent prediction
    results = concurrent_predict_habits(user_id, habits)
    for result in results:
        if result['prediction'] is not None:
            habit_id = result['habit_id']
            prediction_result = result['prediction']
            generated_at = datetime.utcnow().isoformat() + 'Z'
            prediction_id = str(uuid.uuid4())
            db_client.store_prediction(
                user_id=user_id,
                habit_id=habit_id,
                prediction_id=prediction_id,
                generated_at=generated_at,
                prediction_type='rl_time_prediction',
                prediction_value=prediction_result,
                model_id=model_id,
                confidence=1.0
            )
    return jsonify({'message': 'Predictions generated and stored', 'results': results}), 200

@app.route('/api/habit/predictions/get', methods=['GET'])
def get_habit_predictions():
    user_id = request.args.get('user_id')
    habit_id = request.args.get('habit_id')
    predictions = db_client.get_predictions_for_habit(user_id, habit_id)
    return jsonify({'predictions': predictions}), 200

@app.route('/api/habit/predictions/feedback', methods=['GET'])
def get_habit_prediction_feedback():
    user_id = request.args.get('user_id')
    habit_id = request.args.get('habit_id')
    predictions = db_client.get_predictions_for_habit(user_id, habit_id)
    if not predictions:
        return jsonify({'error': 'No predictions found'}), 404
    predictor = HabitPredictor()
    feedbacks = []
    for pred in predictions:
        feedback = predictor.get_prediction_feedback(pred['PredictionValue'])
        feedbacks.append({'prediction_id': pred['SK'], 'feedback': feedback})
    return jsonify({'feedbacks': feedbacks}), 200

@app.route('/api/habit/predictions/rl_train', methods=['POST'])
def train_rl_model():
    data = request.json
    user_id = data['user_id']
    habit_id = data['habit_id']
    logs = db_client.get_logs_for_habit(user_id, habit_id)
    predictor = HabitPredictor()
    predictor.rl_agent.train_from_logs(logs)
    return jsonify({'message': 'RL model trained for habit', 'habit_id': habit_id}), 200

# Run Flask App
if __name__ == '__main__':
    app.run(debug=True)
