from django.conf import settings
from learning.models import Course
from learning.utils import compute_overall_points, streak_ratio
from .ml_engine import MLService, recommend_courses


def _level_from_points(overall_points):
    if overall_points < 50:
        return 'Beginner'
    if overall_points < 75:
        return 'Intermediate'
    return 'Advanced'


def _content_only_recommend(topic, level, top_k=5):
    level_to_diff = {
        'Beginner': 'easy',
        'Intermediate': 'medium',
        'Advanced': 'hard',
    }
    target_diff = level_to_diff.get(level, 'easy')

    primary = list(Course.objects.filter(topic__iexact=topic))
    secondary = list(Course.objects.exclude(topic__iexact=topic))
    pool = primary + secondary

    def score(course):
        points = 0
        reasons = []
        if course.topic.lower() == topic.lower():
            points += 3
            reasons.append('Matches your selected topic')
        if course.difficulty == target_diff:
            points += 2
            reasons.append(f'Aligned with your current level ({level})')
        return points, reasons

    ranked = []
    for course in pool:
        points, reasons = score(course)
        ranked.append(
            {
                'id': course.id,
                'title': course.title,
                'topic': course.topic,
                'difficulty': course.difficulty,
                'description': course.description,
                'url': course.url,
                'why_recommended': '; '.join(reasons) if reasons else 'Recommended by fallback content matching',
                '_score': points,
            }
        )

    ranked.sort(key=lambda item: item['_score'], reverse=True)
    results = ranked[:top_k]
    for item in results:
        item.pop('_score', None)
    return results


def infer_level_and_recommend(topic, correct_count, total_questions, total_time, correctness):
    total_questions = max(total_questions, 1)
    avg_score = (correct_count / total_questions) * 100
    avg_time = total_time / total_questions
    consistency = streak_ratio(correctness)
    overall_points = compute_overall_points(
        correct_count=correct_count,
        total_questions=total_questions,
        total_time=total_time,
        correctness=correctness,
        target_time=settings.TARGET_TIME_PER_QUESTION,
    )

    try:
        ml = MLService.get_instance()
        level = ml.predict_level(
            avg_score=avg_score,
            avg_time=avg_time,
            consistency=consistency,
            overall_points=overall_points,
            topic=topic,
        )

        courses = recommend_courses(
            topic=topic,
            level=level,
            avg_score=avg_score,
            avg_time=avg_time,
            consistency=consistency,
            overall_points=overall_points,
            top_k=5,
        )
    except Exception:
        level = _level_from_points(overall_points)
        courses = _content_only_recommend(topic, level, top_k=5)

    return level, courses
