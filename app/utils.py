from functools import lru_cache
from app.settings import GameSettings


@lru_cache
def get_settings():
    return GameSettings()

def validate_and_normalize_viewport(payload: dict) -> dict:
    settings = get_settings()

    # Ensure that values have been sent, if not, use the default values
    try:
        requested_x = int(payload.get("x", 0))
        requested_y = int(payload.get("y", 0))
        requested_rows = int(payload.get("rows", settings.rows))
        requested_cols = int(payload.get("cols", settings.cols))
    except (TypeError, ValueError):
        raise ValueError("Viewport fields must be integers")

    if requested_rows <= 0 or requested_cols <= 0:
        raise ValueError("Viewport rows/cols must be > 0")
    if requested_rows * requested_cols > settings.max_viewport_cells:
        raise ValueError("Requested viewport area too large")

    # Wrap around coordinates for toroidal behavior
    wrapped_x = requested_x % settings.cols
    wrapped_y = requested_y % settings.rows

    # Clamp viewport size to world dimensions
    clamped_rows = min(requested_rows, settings.rows)
    clamped_cols = min(requested_cols, settings.cols)

    return {
        "x": wrapped_x,
        "y": wrapped_y,
        "rows": clamped_rows,
        "cols": clamped_cols
    }
