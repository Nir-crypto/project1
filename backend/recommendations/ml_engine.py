from pathlib import Path
import numpy as np
import pandas as pd
import joblib
from django.conf import settings
from learning.models import Course


LEVEL_TO_DIFFICULTY = {
    'Beginner': 'easy',
    'Intermediate': 'medium',
    'Advanced': 'hard',
}


class MLService:
    _instance = None

    def __init__(self):
        artifact_dir = Path(settings.ML_ARTIFACT_DIR)
        self.random_forest = joblib.load(artifact_dir / 'random_forest.joblib')
        self.decision_tree = joblib.load(artifact_dir / 'decision_tree.joblib')
        self.knn = joblib.load(artifact_dir / 'knn.joblib')
        self.scaler = joblib.load(artifact_dir / 'scaler.joblib')
        self.topic_encoder = joblib.load(artifact_dir / 'topic_encoder.joblib')
        self.skill_encoder = joblib.load(artifact_dir / 'skill_encoder.joblib')
        self.history_meta = joblib.load(artifact_dir / 'history_meta.joblib')

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = MLService()
        return cls._instance

    def _build_feature(self, avg_score, avg_time, consistency, overall_points, topic):
        safe_topic = topic if topic in self.topic_encoder.classes_ else self.topic_encoder.classes_[0]
        topic_encoded = self.topic_encoder.transform([safe_topic])[0]
        return np.array([[avg_score, avg_time, consistency, overall_points, topic_encoded]], dtype=float)

    def predict_level(self, avg_score, avg_time, consistency, overall_points, topic):
        feature = self._build_feature(avg_score, avg_time, consistency, overall_points, topic)
        scaled = self.scaler.transform(feature)

        rf_pred = self.random_forest.predict(scaled)[0]
        dt_pred = self.decision_tree.predict(scaled)[0]

        pred = rf_pred if rf_pred == dt_pred else rf_pred
        level = self.skill_encoder.inverse_transform([int(pred)])[0]
        return level

    def neighbor_profile(self, avg_score, avg_time, consistency, overall_points, topic, n_neighbors=5):
        feature = self._build_feature(avg_score, avg_time, consistency, overall_points, topic)
        scaled = self.scaler.transform(feature)
        _, indices = self.knn.kneighbors(scaled, n_neighbors=n_neighbors)
        meta = self.history_meta.iloc[indices[0]]
        return meta


def align_difficulty_score(course_difficulty, target_difficulty):
    order = ['easy', 'medium', 'hard']
    a = order.index(course_difficulty)
    b = order.index(target_difficulty)
    diff = abs(a - b)
    if diff == 0:
        return 3
    if diff == 1:
        return 1
    return 0


def recommend_courses(topic, level, avg_score, avg_time, consistency, overall_points, top_k=5):
    ml = MLService.get_instance()
    neighbors = ml.neighbor_profile(avg_score, avg_time, consistency, overall_points, topic)
    neighbor_topic_counts = neighbors['topic'].value_counts().to_dict()
    neighbor_skill_counts = neighbors['skill_label'].value_counts().to_dict()
    dominant_skill = max(neighbor_skill_counts, key=neighbor_skill_counts.get)

    target_difficulty = LEVEL_TO_DIFFICULTY.get(level, 'easy')
    dominant_difficulty = LEVEL_TO_DIFFICULTY.get(dominant_skill, target_difficulty)

    scored = []
    for course in Course.objects.all():
        reasons = []
        score = 0

        if course.topic.lower() == topic.lower():
            score += 4
            reasons.append('Matches your selected topic')

        diff_score = align_difficulty_score(course.difficulty, target_difficulty)
        score += diff_score
        if diff_score >= 3:
            reasons.append(f"Aligned with your current level ({level})")
        elif diff_score == 1:
            reasons.append('Slightly challenges your current level')

        if neighbor_topic_counts.get(course.topic, 0) > 0:
            score += 2
            reasons.append('Popular among learners with similar performance')

        if align_difficulty_score(course.difficulty, dominant_difficulty) >= 1:
            score += 1
            reasons.append('Fits paths taken by similar learners')

        if score > 0:
            scored.append(
                {
                    'id': course.id,
                    'title': course.title,
                    'topic': course.topic,
                    'difficulty': course.difficulty,
                    'description': course.description,
                    'url': course.url,
                    'why_recommended': '; '.join(dict.fromkeys(reasons)) or 'Strong overall fit for your profile',
                    '_score': score,
                }
            )

    scored.sort(key=lambda item: item['_score'], reverse=True)
    results = scored[:top_k]
    for item in results:
        item.pop('_score', None)
    return results
