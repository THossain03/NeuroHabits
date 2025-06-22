import numpy as np
from collections import defaultdict
import pickle
from datetime import datetime
from .config.db_config import get_db_config

class HabitRLAgent:
    def __init__(self, alpha=None, gamma=None, epsilon=None):
        config = get_db_config()
        self.alpha = alpha if alpha is not None else config.rl_alpha
        self.gamma = gamma if gamma is not None else config.rl_gamma
        self.epsilon = epsilon if epsilon is not None else config.rl_epsilon
        self.q_table = defaultdict(lambda: defaultdict(float))  # state -> action -> value

    def state_from_time(self, dt: datetime):
        # State: (hour, day, weekday)
        return (dt.hour, dt.day, dt.weekday())

    def choose_action(self, state):
        # For prediction: choose best action (0=skip, 1=do)
        if np.random.rand() < self.epsilon:
            return np.random.choice([0, 1])
        q_vals = self.q_table[state]
        return max(q_vals, key=q_vals.get, default=1)

    def update(self, state, action, reward, next_state):
        best_next = max(self.q_table[next_state].values(), default=0)
        old_value = self.q_table[state][action]
        self.q_table[state][action] += self.alpha * (reward + self.gamma * best_next - old_value)

    def train_from_logs(self, logs):
        # logs: list of dicts with 'LoggedAt' and 'Status'
        for i in range(len(logs) - 1):
            dt = datetime.fromisoformat(logs[i]['LoggedAt'])
            state = self.state_from_time(dt)
            action = 1 if logs[i]['Status'] == 'COMPLETED' else 0
            reward = 1 if action == 1 else -1
            next_dt = datetime.fromisoformat(logs[i+1]['LoggedAt'])
            next_state = self.state_from_time(next_dt)
            self.update(state, action, reward, next_state)

    def predict_next(self, current_time=None):
        # Predict best action for current time
        if current_time is None:
            current_time = datetime.utcnow()
        state = self.state_from_time(current_time)
        action = self.choose_action(state)
        return action, dict(self.q_table[state])

    def serialize(self):
        return pickle.dumps(dict(self.q_table))

    def deserialize(self, data):
        self.q_table = defaultdict(lambda: defaultdict(float), pickle.loads(data)) 