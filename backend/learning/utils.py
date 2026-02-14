from typing import List
import math

DIFFICULTY_ORDER = ['easy', 'medium', 'hard']
LEVEL_BY_DIFFICULTY = {
    'easy': 'Beginner',
    'medium': 'Intermediate',
    'hard': 'Advanced',
}


def clamp_difficulty(current: str, is_correct: bool) -> str:
    idx = DIFFICULTY_ORDER.index(current) if current in DIFFICULTY_ORDER else 0
    if is_correct:
        idx = min(idx + 1, len(DIFFICULTY_ORDER) - 1)
    else:
        idx = max(idx - 1, 0)
    return DIFFICULTY_ORDER[idx]


def streak_ratio(correctness: List[bool]) -> float:
    if not correctness:
        return 0.0
    max_streak = 0
    streak = 0
    for value in correctness:
        if value:
            streak += 1
            max_streak = max(max_streak, streak)
        else:
            streak = 0
    return max_streak / len(correctness)


def compute_overall_points(correct_count: int, total_questions: int, total_time: float, correctness: List[bool], target_time: float) -> float:
    accuracy = correct_count / total_questions if total_questions else 0.0
    avg_time = total_time / total_questions if total_questions else 0.0
    time_factor = max(0.0, min(1.0, 1 - (avg_time / target_time))) if target_time > 0 else 0.0
    consistency = streak_ratio(correctness)
    score = 70 * accuracy + 20 * time_factor + 10 * consistency
    return round(score, 2)


def safe_option(option: str) -> str:
    option = (option or '').lower().strip()
    return option if option in {'a', 'b', 'c', 'd'} else ''
