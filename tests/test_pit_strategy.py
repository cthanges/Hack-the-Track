from src.analytics.pit_strategy import recommend_pit


def test_recommend_when_stint_reached():
    rec = recommend_pit(current_lap=21, last_pit_lap=1, last_laps_seconds=[100, 99, 101], target_stint=20, pit_time_cost=20)
    assert rec['recommended_lap'] == 22 or rec['recommended_lap'] == 21


def test_no_net_gain():
    rec = recommend_pit(current_lap=5, last_pit_lap=3, last_laps_seconds=[120, 121], target_stint=10, pit_time_cost=100)
    assert rec['recommended_lap'] is None
