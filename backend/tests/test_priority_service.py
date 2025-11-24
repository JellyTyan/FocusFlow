import pytest
from datetime import datetime, timedelta
from services.priority_service import calculate_priority, calculate_days_to_deadline

def test_calculate_priority_basic():
    """Test basic priority calculation"""
    priority = calculate_priority(confidence_level=2, stuck_count=0, days_to_deadline=10)
    assert priority > 0
    assert isinstance(priority, float)

def test_calculate_priority_low_confidence():
    """Test that low confidence increases priority"""
    low_conf = calculate_priority(confidence_level=1, stuck_count=0, days_to_deadline=10)
    high_conf = calculate_priority(confidence_level=5, stuck_count=0, days_to_deadline=10)
    assert low_conf > high_conf

def test_calculate_priority_stuck_count():
    """Test that stuck count increases priority"""
    no_stuck = calculate_priority(confidence_level=3, stuck_count=0, days_to_deadline=10)
    with_stuck = calculate_priority(confidence_level=3, stuck_count=5, days_to_deadline=10)
    assert with_stuck > no_stuck

def test_calculate_priority_deadline():
    """Test that closer deadline increases priority"""
    far = calculate_priority(confidence_level=3, stuck_count=0, days_to_deadline=30)
    close = calculate_priority(confidence_level=3, stuck_count=0, days_to_deadline=3)
    assert close > far

def test_calculate_priority_zero_days():
    """Test that zero or negative days defaults to 1"""
    priority = calculate_priority(confidence_level=3, stuck_count=0, days_to_deadline=0)
    assert priority > 0

def test_calculate_days_to_deadline():
    """Test days calculation"""
    future = datetime.now() + timedelta(days=5)
    days = calculate_days_to_deadline(future)
    assert 4 <= days <= 5  # Allow for timing differences