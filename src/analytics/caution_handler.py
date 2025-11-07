from typing import Dict


def recommend_under_caution(current_recommendation: Dict, pit_time_cost: float = 20.0, caution_pit_factor: float = 0.5) -> Dict:
    """Adjust a pit recommendation when a caution occurs.

    The model reduces the effective pit cost under caution by caution_pit_factor (e.g. 0.5)
    and suggests pitting if a previously no-net-gain recommendation becomes positive.
    """
    effective_cost = pit_time_cost * caution_pit_factor
    # if there was previously no recommended pit, create a simple check
    if current_recommendation.get('recommended_lap') is None:
        # very simple rule: if effective cost is low (<10s), recommend pitting now
        if effective_cost < 10:
            return {"action": "pit_now", "reason": "caution_reduces_cost", "effective_cost": effective_cost}
        return {"action": "stay", "reason": "caution_not_beneficial", "effective_cost": effective_cost}

    # if there was a recommended future lap, it's usually beneficial to pit now under caution
    return {"action": "pit_now", "reason": "existing_recommendation_preempted", "effective_cost": effective_cost}
