from datetime import datetime
from collections import Counter, defaultdict
import numpy as np

def extract_time_features(logs):
    features = []
    for log in logs:
        dt = datetime.fromisoformat(log['LoggedAt'])
        features.append({
            'hour': dt.hour,
            'day': dt.day,
            'month': dt.month,
            'weekday': dt.weekday(),
            'status': log['Status']
        })
    return features

def compute_frequency_stats(logs):
    # Returns dict: {period: count}
    hour_counts = Counter()
    weekday_counts = Counter()
    month_counts = Counter()
    for log in logs:
        dt = datetime.fromisoformat(log['LoggedAt'])
        hour_counts[dt.hour] += 1
        weekday_counts[dt.weekday()] += 1
        month_counts[dt.month] += 1
    return {
        'hourly': hour_counts,
        'weekday': weekday_counts,
        'monthly': month_counts
    }

def summarize_habit_stats(stats):
    # stats: dict from HabitStats table
    summary = {
        'total': stats.get('TotalCount', 0),
        'streak': stats.get('StreakCurrent', 0),
        'best_streak': stats.get('StreakBest', 0),
        'success_rate': stats.get('SuccessRate', 0.0),
        'missed': stats.get('MissedCount', 0)
    }
    return summary 