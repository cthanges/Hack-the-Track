from src.analytics.pit_strategy import recommend_pit


def test_optimal_window_finds_best_lap():
    """Test that optimizer finds pit lap that minimizes total time."""
    rec = recommend_pit(
        current_lap=10,
        last_pit_lap=1,
        last_laps_seconds=[90.0, 90.5, 91.0],  # Degrading
        target_stint=20,
        pit_time_cost=20.0,
        remaining_laps=15,
        degradation_per_lap=0.2
    )
    # Should recommend a pit lap (degradation makes it worthwhile)
    assert rec['recommended_lap'] is not None
    assert rec['score'] > 0  # Should save time
    assert 'candidates' in rec
    assert len(rec['candidates']) > 0


def test_no_pit_when_too_few_laps():
    """Test that no pit is recommended when very few laps remain."""
    rec = recommend_pit(
        current_lap=48,
        last_pit_lap=30,
        last_laps_seconds=[90.0, 90.2],
        target_stint=20,
        pit_time_cost=20.0,
        remaining_laps=2
    )
    assert rec['recommended_lap'] is None
    assert rec['reason'] == 'too_few_laps_remaining'


def test_no_pit_when_cost_too_high():
    """Test that no pit is recommended when pit cost exceeds benefit."""
    rec = recommend_pit(
        current_lap=10,
        last_pit_lap=5,
        last_laps_seconds=[90.0, 90.1],
        target_stint=20,
        pit_time_cost=100.0,  # Very expensive pit
        remaining_laps=10,
        degradation_per_lap=0.1  # Low degradation
    )
    assert rec['recommended_lap'] is None
    assert rec['reason'] == 'no_net_benefit'


def test_finds_optimal_lap_in_window():
    """Test that optimizer evaluates multiple candidates and picks best."""
    rec = recommend_pit(
        current_lap=10,
        last_pit_lap=1,
        last_laps_seconds=[90.0, 90.5, 91.0],
        target_stint=20,
        pit_time_cost=15.0,
        remaining_laps=20,
        degradation_per_lap=0.3  # High degradation
    )
    assert rec['recommended_lap'] is not None
    assert len(rec['candidates']) > 1  # Multiple candidates evaluated
    # Verify best candidate is chosen
    best_candidate = min(rec['candidates'], key=lambda c: c['expected_time'])
    assert rec['recommended_lap'] == best_candidate['pit_lap']
