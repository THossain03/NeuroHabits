import boto3
from botocore.exceptions import ClientError
from embeddings import store_habit_embedding, get_habit_embedding
from rl_models import HabitRLAgent
from ml_models import HabitPredictor
from prediction_utils import compute_frequency_stats

# Sample Initialization of DynamoDB (TODO: set up still in progress)
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')  # TODO: Replace with dynamic region configuration later. Apply us-east-1 for now solely during in dev.

def test_embedding_storage():
    user_id = 'testuser'
    habit_id = 'habit1'
    text = 'Drink water every morning'
    table_name = 'Habits'
    store_habit_embedding(user_id, habit_id, text, table_name)
    emb = get_habit_embedding(user_id, habit_id, table_name)
    assert emb is not None
    print('Embedding storage and retrieval test passed.')

def test_rl_agent_training_and_prediction():
    logs = [
        {'LoggedAt': '2024-06-01T08:00:00', 'Status': 'COMPLETED'},
        {'LoggedAt': '2024-06-02T08:00:00', 'Status': 'MISSED'},
        {'LoggedAt': '2024-06-03T08:00:00', 'Status': 'COMPLETED'}
    ]
    agent = HabitRLAgent()
    agent.train_from_logs(logs)
    action, q_values = agent.predict_next()
    assert isinstance(action, int)
    assert isinstance(q_values, dict)
    print('RL agent training and prediction test passed.')

def test_habit_predictor_feedback():
    logs = [
        {'LoggedAt': '2024-06-01T08:00:00', 'Status': 'COMPLETED'},
        {'LoggedAt': '2024-06-02T08:00:00', 'Status': 'MISSED'},
        {'LoggedAt': '2024-06-03T08:00:00', 'Status': 'COMPLETED'}
    ]
    predictor = HabitPredictor()
    result = predictor.train_and_predict(logs)
    feedback = predictor.get_prediction_feedback(result)
    assert isinstance(feedback, str)
    print('HabitPredictor feedback test passed.')