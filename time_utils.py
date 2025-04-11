import time
from datetime import datetime, timedelta

def estimate_time_left(start_time_dt, processed_count, total_count):
    """
    Estimates the time left to process the remaining items, accepting a datetime object
    as the start time.

    Args:
        start_time_dt (datetime): The datetime object representing when processing started.
        processed_count (int): The number of items processed so far.
        total_count (int): The total number of items to be processed.

    Returns:
        timedelta or None: A timedelta object representing the estimated time left,
                        or None if no items have been processed yet.
    """
    if processed_count > 0:
        elapsed_time_seconds = (datetime.now() - start_time_dt).total_seconds()
        average_time_per_item = elapsed_time_seconds / processed_count
        remaining_items = total_count - processed_count
        estimated_time_seconds = remaining_items * average_time_per_item
        return timedelta(seconds=estimated_time_seconds)
    else:
        return None
