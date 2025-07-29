"""
Standardized chart sizing utility for dashboard visual harmony.
"""

def get_standard_chart_height(num_items: int, base_height: int = 400, row_scale: int = 22, min_height: int = 400, max_height: int = 800) -> int:
    """
    Calculate a standard chart height based on the number of items (rows/bars/lines).
    Ensures charts are visually balanced and consistent across the dashboard.

    Args:
        num_items (int): Number of items to display (e.g., bars, rows).
        base_height (int): Base height for charts with few items.
        row_scale (int): Additional height per item.
        min_height (int): Minimum allowed height.
        max_height (int): Maximum allowed height.

    Returns:
        int: Calculated chart height in pixels.
    """
    if num_items is None or num_items <= 0:
        return base_height
    height = base_height + row_scale * num_items
    return max(min_height, min(height, max_height))
