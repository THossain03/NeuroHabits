from concurrent.futures import ThreadPoolExecutor, as_completed
from .ml_models import HabitPredictor
from .db.dynamo_client import db_client

def concurrent_predict_habits(user_id, habits, max_workers=4):
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_habit = {
            executor.submit(predict_for_habit, user_id, habit['HabitID']): habit['HabitID']
            for habit in habits
        }
        for future in as_completed(future_to_habit):
            habit_id = future_to_habit[future]
            try:
                result = future.result()
                results.append({'habit_id': habit_id, 'prediction': result})
            except Exception as exc:
                results.append({'habit_id': habit_id, 'error': str(exc)})
    return results

def predict_for_habit(user_id, habit_id):
    logs = db_client.get_logs_for_habit(user_id, habit_id)
    if not logs:
        return None
    predictor = HabitPredictor()
    return predictor.train_and_predict(logs) 