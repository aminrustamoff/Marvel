def get_listening_band(correct_count):
    """Maps the raw score (0-40) to IELTS Band Scores."""
    if correct_count >= 39: return 9.0
    if correct_count >= 37: return 8.5
    if correct_count >= 35: return 8.0
    if correct_count >= 32: return 7.5
    if correct_count >= 30: return 7.0
    if correct_count >= 26: return 6.5
    if correct_count >= 23: return 6.0
    if correct_count >= 18: return 5.5
    if correct_count >= 16: return 5.0
    if correct_count >= 13: return 4.5
    if correct_count >= 10: return 4.0
    if correct_count >= 8: return 3.5
    if correct_count >= 6: return 3.0
    if correct_count >= 4: return 2.5
    if correct_count >= 2: return 2.0
    if correct_count >= 1: return 1.5
    if correct_count >= 0: return 1.0
    return 0.0 # Minimum threshold

def get_reading_band(correct_count):
    """Maps the raw score (0-40) to IELTS Band Scores."""
    if correct_count >= 39: return 9.0
    if correct_count >= 37: return 8.5
    if correct_count >= 35: return 8.0
    if correct_count >= 33: return 7.5
    if correct_count >= 30: return 7.0
    if correct_count >= 27: return 6.5
    if correct_count >= 23: return 6.0
    if correct_count >= 19: return 5.5
    if correct_count >= 15: return 5.0
    if correct_count >= 13: return 4.5
    if correct_count >= 10: return 4.0
    if correct_count >= 8: return 3.5
    if correct_count >= 6: return 3.0
    if correct_count >= 4: return 2.5
    if correct_count >= 2: return 2.0
    if correct_count >= 1: return 1.5
    if correct_count >= 0: return 1.0
    return 0.0 # Minimum threshold