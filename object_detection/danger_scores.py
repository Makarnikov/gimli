# danger_scores.py

DANGER_SCORES = {
    'knife': 0.6,
    'scissors': 0.4,
    'human': 0.9,
    'table': 0.0,
    'floor': 0.0,
    'wall': 0.0,
}


def get_danger_score(label: str) -> float:
    return DANGER_SCORES.get(label.lower(), 0.0)
