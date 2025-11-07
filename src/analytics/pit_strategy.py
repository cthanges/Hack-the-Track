from typing import List, Dict
import numpy as np


def recommend_pit(current_lap: int,
                  last_pit_lap: int,
                  last_laps_seconds: List[float],
                  target_stint: int = 20,
                  pit_time_cost: float = 20.0) -> Dict:
    """Simple heuristic recommendation for pit lap.

    - If current stint (current_lap - last_pit_lap) >= target_stint, recommend next lap.
    - Otherwise use last laps to estimate degradation and see if pitting earlier returns net gain.
    Returns dict: {recommended_lap, reason, score}
    """
    stint = current_lap - last_pit_lap
    avg_last = float(np.mean(last_laps_seconds)) if len(last_laps_seconds) else 0.0

    # baseline: recommend pitting if stint length reached
    if stint >= target_stint:
        return {"recommended_lap": current_lap + 1, "reason": "stint_target_reached", "score": 1.0}

    # estimate fresh-tyre advantage: assume first 3 laps on fresh tyres are faster by a fixed delta
    fresh_delta = 2.0  # seconds faster when fresh (very simple proxy)
    expected_gain_if_pit = fresh_delta * 3 - pit_time_cost

    score = expected_gain_if_pit
    if expected_gain_if_pit < 0:
        return {"recommended_lap": None, "reason": "no_net_gain", "score": score}

    # recommend earliest lap within a short window where pit makes sense
    recommended = current_lap + 1
    return {"recommended_lap": recommended, "reason": "net_gain_positive", "score": score}
