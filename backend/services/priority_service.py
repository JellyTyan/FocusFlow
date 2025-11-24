from datetime import datetime

def calculate_priority(confidence_level: int, stuck_count: int, days_to_deadline: int) -> float:
    """Calculate topic priority based on confidence, stuck count, and deadline"""
    if days_to_deadline <= 0:
        days_to_deadline = 1
    
    confidence_factor = 6 - confidence_level
    stuck_multiplier = 1 + (stuck_count * 0.2)
    
    return (1 / days_to_deadline) * confidence_factor * stuck_multiplier

def calculate_days_to_deadline(deadline: datetime) -> int:
    """Calculate days remaining until deadline"""
    return (deadline - datetime.now()).days