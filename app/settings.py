# app/settings.py
from pydantic import Field, PositiveInt, PositiveFloat
from pydantic_settings import BaseSettings

class GameSettings(BaseSettings):
    rows: PositiveInt = Field(default=500, validate_default=True, description="Total number of rows in the world")
    cols: PositiveInt = Field(default=700, validate_default=True, description="Total number of columns in the world")
    speed: PositiveFloat = Field(default=0.2, validate_default=True, description="Game speed (seconds per step)")
    cell_color: str = Field(default="#4CAF50", description="Color of living cells")
    bg_color: str = Field(default="#111", description="Background color of the canvas")
    max_viewport_cells: PositiveInt = Field(default=200_000, validate_default=True, description="Maximum number of cells in the viewport")

    class Config:
        env_prefix = "GAME_"  # Allows overriding from .env using those prefixed with "GAME_". Example: GAME_ROWS=1000
