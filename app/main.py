from pathlib import Path

from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.game_of_life import GameOfLife
import asyncio, json

app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

# Serving static files (frontend)
app.mount("/public", StaticFiles(directory=STATIC_DIR), name="public")

game = GameOfLife(height=30, width=50)
game.randomize()

@app.get("/")
async def root():
    return FileResponse(STATIC_DIR / "index.html")

# WebSocket to send the grid in real time
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            grid = game.step()
            await ws.send_text(json.dumps(grid))
            await asyncio.sleep(0.2)  # Here you can change the speed of the game
    except Exception:
        await ws.close()
