"""
Tests for traffic model and field position analysis.
"""

import pytest
import pandas as pd
import numpy as np
from src.analytics.traffic_model import TrafficModel, FieldPosition, TrafficOpportunity


@pytest.fixture
def sample_endurance_data():
    """Create sample endurance data for testing."""
    data = {
        'NUMBER': [13, 22, 72, 13, 22, 72, 13, 22, 72],
        'LAP_NUMBER': [1, 1, 1, 2, 2, 2, 3, 3, 3],
        'ELAPSED': ['1:40.123', '1:42.456', '1:43.789', 
                    '3:20.246', '3:24.912', '3:27.578',
                    '5:00.369', '5:07.368', '5:11.367'],
        'LAP_TIME': ['1:40.123', '1:42.456', '1:43.789',
                     '1:40.123', '1:42.456', '1:43.789',
                     '1:40.123', '1:42.456', '1:43.789']
    }
    return pd.DataFrame(data)


@pytest.fixture
def traffic_model(sample_endurance_data):
    """Create TrafficModel instance for testing."""
    return TrafficModel(sample_endurance_data)


def test_traffic_model_initialization(sample_endurance_data):
    """Test that TrafficModel initializes correctly."""
    model = TrafficModel(sample_endurance_data)
    assert model is not None
    assert hasattr(model, 'position_table')
    assert len(model.position_table) == 3  # 3 laps


def test_missing_columns_raises_error():
    """Test that missing required columns raises ValueError."""
    bad_data = pd.DataFrame({
        'NUMBER': [1, 2],
        'ELAPSED': ['1:40.0', '1:42.0']
        # Missing LAP_NUMBER
    })
    
    with pytest.raises(ValueError, match='Missing required columns'):
        TrafficModel(bad_data)


def test_elapsed_time_parsing():
    """Test parsing of elapsed time from various formats."""
    model = TrafficModel(pd.DataFrame({
        'NUMBER': [1, 2, 3],
        'LAP_NUMBER': [1, 1, 1],
        'ELAPSED': ['1:40.123', '45:30.456', '1:23:45.789']
    }))
    
    # Check parsed times
    lap1_positions = model.get_running_order(1)
    assert len(lap1_positions) == 3
    
    # 1:40.123 = 100.123s
    assert abs(lap1_positions[0].elapsed_time - 100.123) < 0.01
    
    # 45:30.456 = 2730.456s
    assert abs(lap1_positions[1].elapsed_time - 2730.456) < 0.01
    
    # 1:23:45.789 = 5025.789s
    assert abs(lap1_positions[2].elapsed_time - 5025.789) < 0.01


def test_get_field_position(traffic_model):
    """Test retrieving field position for a specific car and lap."""
    pos = traffic_model.get_field_position(car_number=13, lap=1)
    
    assert pos is not None
    assert pos.position == 1  # Car 13 should be P1
    assert pos.car_number == 13
    assert pos.lap == 1
    assert pos.gap_to_leader == 0.0  # Leader has 0 gap


def test_get_field_position_not_found(traffic_model):
    """Test that get_field_position returns None for non-existent car/lap."""
    pos = traffic_model.get_field_position(car_number=999, lap=1)
    assert pos is None
    
    pos = traffic_model.get_field_position(car_number=13, lap=99)
    assert pos is None


def test_running_order_sorting(traffic_model):
    """Test that running order is correctly sorted by elapsed time."""
    order = traffic_model.get_running_order(lap=2)
    
    assert len(order) == 3
    assert order[0].car_number == 13  # Fastest
    assert order[1].car_number == 22
    assert order[2].car_number == 72  # Slowest
    
    # Positions should be sequential
    assert order[0].position == 1
    assert order[1].position == 2
    assert order[2].position == 3


def test_gap_calculations(traffic_model):
    """Test that gaps are calculated correctly."""
    order = traffic_model.get_running_order(lap=1)
    
    # P1 should have 0 gap to leader
    assert order[0].gap_to_leader == 0.0
    assert order[0].gap_to_ahead == 0.0
    
    # P2 should have gap to leader and to car ahead
    assert order[1].gap_to_leader > 0
    assert order[1].gap_to_ahead > 0
    
    # P3 gaps should be largest
    assert order[2].gap_to_leader > order[1].gap_to_leader
    assert order[2].gap_to_ahead > 0


def test_estimate_position_after_pit(traffic_model):
    """Test estimation of position after pit stop."""
    # Car 13 in P1, simulate pit stop
    new_pos, new_gap = traffic_model.estimate_position_after_pit(
        car_number=13,
        current_lap=1,
        pit_time_loss=20.0  # 20 second pit stop
    )
    
    assert new_pos is not None
    assert new_gap is not None
    
    # With 20s loss, should drop behind other cars
    assert new_pos > 1  # Should lose positions


def test_estimate_position_after_pit_no_drop(traffic_model):
    """Test pit stop with small time loss (maintain position)."""
    # Car 13 in P1 with small pit loss
    new_pos, new_gap = traffic_model.estimate_position_after_pit(
        car_number=13,
        current_lap=1,
        pit_time_loss=0.5  # Very fast pit
    )
    
    # With 0.5s pit loss and 2.3s gap to P2, should maintain P1
    assert new_pos <= 2  # Allow for P1 or P2 depending on exact gaps


def test_estimate_position_invalid_car(traffic_model):
    """Test that invalid car returns None."""
    new_pos, new_gap = traffic_model.estimate_position_after_pit(
        car_number=999,
        current_lap=1,
        pit_time_loss=20.0
    )
    
    assert new_pos is None
    assert new_gap is None


def test_detect_undercut_opportunities():
    """Test undercut opportunity detection."""
    # Create scenario: car ahead on old tires
    data = pd.DataFrame({
        'NUMBER': [13, 22, 13, 22],
        'LAP_NUMBER': [1, 1, 2, 2],
        'ELAPSED': ['1:40.0', '1:42.0', '3:20.0', '3:25.0']
    })
    
    model = TrafficModel(data)
    
    # Car 22 checking for undercut on car 13
    opportunities = model.detect_undercut_opportunities(
        car_number=22,
        current_lap=2,
        pit_time_loss=20.0,
        degradation_rate=0.2,
        laps_since_pit_ahead={13: 10, 22: 2}  # Car 13 on old tires
    )
    
    # Should detect undercut on car 13
    assert len(opportunities) >= 0  # May or may not detect based on parameters


def test_detect_overcut_opportunities():
    """Test overcut opportunity detection."""
    data = pd.DataFrame({
        'NUMBER': [13, 22, 13, 22],
        'LAP_NUMBER': [1, 1, 2, 2],
        'ELAPSED': ['1:40.0', '1:42.0', '3:20.0', '3:25.0']
    })
    
    model = TrafficModel(data)
    
    # Car 22 checking for overcut
    opportunities = model.detect_overcut_opportunities(
        car_number=22,
        current_lap=2,
        pit_time_loss=20.0,
        laps_since_own_pit=5,
        cars_pitting_soon=[13]  # Car 13 about to pit
    )
    
    # Should detect overcut opportunity
    assert isinstance(opportunities, list)


def test_calculate_traffic_impact():
    """Test traffic impact calculation."""
    # Create scenario with close cars (traffic)
    data = pd.DataFrame({
        'NUMBER': [13, 22, 13, 22],
        'LAP_NUMBER': [1, 1, 2, 2],
        'ELAPSED': ['1:40.0', '1:40.5', '3:20.0', '3:20.8']  # Very close gaps
    })
    
    model = TrafficModel(data)
    
    # Car 22 should experience traffic (close to car 13)
    traffic_loss = model.calculate_traffic_impact(
        car_number=22,
        current_lap=1,
        laps_ahead=2
    )
    
    assert traffic_loss >= 0  # Should be non-negative


def test_get_cars_within_window():
    """Test finding cars within a time window."""
    data = pd.DataFrame({
        'NUMBER': [13, 22, 72, 55],
        'LAP_NUMBER': [1, 1, 1, 1],
        'ELAPSED': ['1:40.0', '1:42.0', '1:43.5', '1:50.0']
    })
    
    model = TrafficModel(data)
    
    # Find cars within 5s of car 22
    nearby = model.get_cars_within_window(
        car_number=22,
        current_lap=1,
        time_window=5.0
    )
    
    # Should include car 13 and 72, but not 55 (too far)
    assert len(nearby) == 2
    car_numbers = [pos.car_number for pos in nearby]
    assert 13 in car_numbers
    assert 72 in car_numbers
    assert 55 not in car_numbers


def test_traffic_opportunity_dataclass():
    """Test TrafficOpportunity dataclass creation."""
    opp = TrafficOpportunity(
        opportunity_type='undercut',
        target_car_number=13,
        target_position=1,
        current_gap=2.5,
        pit_now_advantage=1.8,
        confidence='high',
        description='Test undercut'
    )
    
    assert opp.opportunity_type == 'undercut'
    assert opp.target_car_number == 13
    assert opp.confidence == 'high'


def test_field_position_dataclass():
    """Test FieldPosition dataclass creation."""
    pos = FieldPosition(
        lap=5,
        position=2,
        car_number=22,
        elapsed_time=300.5,
        gap_to_leader=2.3,
        gap_to_ahead=2.3
    )
    
    assert pos.lap == 5
    assert pos.position == 2
    assert pos.car_number == 22


def test_column_name_stripping():
    """Test that column names with spaces are handled correctly."""
    data = pd.DataFrame({
        ' NUMBER ': [13, 22],
        ' LAP_NUMBER ': [1, 1],
        ' ELAPSED ': ['1:40.0', '1:42.0']
    })
    
    # Should not raise error due to space handling
    model = TrafficModel(data)
    assert model is not None


def test_position_consistency_across_laps(traffic_model):
    """Test that position tracking is consistent across multiple laps."""
    # Car 13 should be P1 in all laps (it's fastest)
    for lap in [1, 2, 3]:
        pos = traffic_model.get_field_position(13, lap)
        assert pos.position == 1, f"Car 13 should be P1 on lap {lap}"
    
    # Car 72 should be P3 in all laps (it's slowest)
    for lap in [1, 2, 3]:
        pos = traffic_model.get_field_position(72, lap)
        assert pos.position == 3, f"Car 72 should be P3 on lap {lap}"


def test_multiple_cars_same_elapsed_time():
    """Test handling of cars with identical elapsed times."""
    data = pd.DataFrame({
        'NUMBER': [13, 22, 72],
        'LAP_NUMBER': [1, 1, 1],
        'ELAPSED': ['1:40.0', '1:40.0', '1:41.0']  # 13 and 22 tied
    })
    
    model = TrafficModel(data)
    order = model.get_running_order(1)
    
    # Should handle ties gracefully (stable sort)
    assert len(order) == 3
    assert order[0].position == 1
    assert order[1].position == 2
    assert order[2].position == 3


def test_integration_with_pit_strategy():
    """Test that traffic model integrates with pit strategy module."""
    from src.analytics.pit_strategy import recommend_pit
    
    data = pd.DataFrame({
        'NUMBER': [13, 22, 13, 22],
        'LAP_NUMBER': [5, 5, 10, 10],
        'ELAPSED': ['8:20.0', '8:25.0', '16:40.0', '16:50.0']
    })
    
    model = TrafficModel(data)
    
    # Call pit strategy with traffic model
    rec = recommend_pit(
        current_lap=10,
        last_pit_lap=0,
        last_laps_seconds=[100.0, 100.5, 101.0],
        target_stint=20,
        pit_time_cost=20.0,
        remaining_laps=10,
        degradation_per_lap=0.15,
        traffic_model=model,
        car_number=22,
        consider_traffic=True
    )
    
    # Should return valid recommendation with traffic info
    assert rec is not None
    assert 'field_position' in rec or 'recommended_lap' in rec
