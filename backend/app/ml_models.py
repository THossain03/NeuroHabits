import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from datetime import datetime
from typing import List, Dict
from .rl_models import HabitRLAgent
from .prediction_utils import compute_frequency_stats

class HabitFrequencyKNN:
    def __init__(self, n_neighbors=3):
        self.knn = KNeighborsClassifier(n_neighbors=n_neighbors)
        self.fitted = False

    def _extract_features(self, logs: List[Dict]) -> np.ndarray:
        # Example: convert timestamps to hour, day, month, etc.
        features = []
        for log in logs:
            dt = datetime.fromisoformat(log['LoggedAt'])
            features.append([
                dt.hour,
                dt.day,
                dt.month,
                dt.weekday()
            ])
        return np.array(features)

    def _extract_labels(self, logs: List[Dict]) -> np.ndarray:
        # Example: label by frequency type (dummy: 0=daily, 1=hourly, 2=monthly, 3=annual)
        # In real use, this should be derived from actual log patterns
        return np.zeros(len(logs))

    def fit(self, logs: List[Dict]):
        X = self._extract_features(logs)
        y = self._extract_labels(logs)
        self.knn.fit(X, y)
        self.fitted = True

    def predict(self, logs: List[Dict]) -> List[str]:
        if not self.fitted:
            raise Exception('Model not fitted!')
        X = self._extract_features(logs)
        preds = self.knn.predict(X)
        freq_map = {0: 'daily', 1: 'hourly', 2: 'monthly', 3: 'annual'}
        return [freq_map.get(int(p), 'unknown') for p in preds]

class HabitPredictor:
    def __init__(self):
        self.rl_agent = HabitRLAgent()

    def train_and_predict(self, logs):
        self.rl_agent.train_from_logs(logs)
        action, q_values = self.rl_agent.predict_next()
        freq_stats = compute_frequency_stats(logs)
        return {
            'rl_action': action,
            'q_values': q_values,
            'frequency_stats': freq_stats
        }

    def get_prediction_feedback(self, prediction_result):
        # Generate feedback string based on prediction result
        freq = prediction_result['frequency_stats']
        qv = prediction_result['q_values']
        if freq['hourly']:
            most_common_hour = freq['hourly'].most_common(1)[0][0]
        else:
            most_common_hour = None
        if freq['weekday']:
            most_common_weekday = freq['weekday'].most_common(1)[0][0]
        else:
            most_common_weekday = None
        feedback = f"You most often complete this habit at hour {most_common_hour} on weekday {most_common_weekday}. RL Q-values: {qv}"
        return feedback 