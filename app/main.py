from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import asyncio, json

from app.game_of_life import GameOfLife
from app.utils import validate_and_normalize_viewport, get_settings
from app.ws_utils import send_json_safe, wait_for_initial_viewport, close_ws_safe, receive_text_with_timeout

app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"

# Serving static files (frontend)
app.mount("/public", StaticFiles(directory=STATIC_DIR), name="public")

settings = get_settings()
game = GameOfLife(height=settings.rows, width=settings.cols)
game.randomize(prob=1)

# Lock to protect concurrent access to game.grid
game_lock = asyncio.Lock()

@app.get("/")
async def root():
    return FileResponse(STATIC_DIR / "index.html")

# WebSocket to send the grid in real time
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()

    # Send the initial game configuration to the client
    sent = await send_json_safe(ws, {
        "type": "config",
        "payload": {
            "rows": settings.rows,
            "cols": settings.cols,
            "speed": settings.speed,
            "cell_color": settings.cell_color,
            "bg_color": settings.bg_color
        }
    })

    if not sent:
        # TODO: Add a logger for further debugging
        print("Failed to send config; closing w")
        await close_ws_safe(ws)
        return

    # Wait for the client's viewport
    # This is done so that the step can be calculated only from what the user sees
    try:
        viewport = await wait_for_initial_viewport(ws)
    except (asyncio.TimeoutError, WebSocketDisconnect) as ex:
        await send_json_safe(ws, {"type": "error", "message": str(ex)})
        await close_ws_safe(ws)
        return
    except Exception:
        await close_ws_safe(ws)
        raise  # let the error propagate if logging is set

    # ACK message: confirm receipt of the viewport
    await send_json_safe(ws, {"type": "ok", "message": "viewport accepted", "viewport": viewport})

    # Main loop: from here, updates are received (new viewport in this case) from the client
    try:
        while True:
            # Wait for a message with a timeout equal to the game speed,
            # this way the game advances at the indicated speed
            raw = await receive_text_with_timeout(ws, timeout=settings.speed)

            # If no message arrived within the timeout, we calculate the step with the user's current viewport
            if raw is None:
                async with game_lock:
                    visible = game.step(
                        viewport_x=viewport["x"],
                        viewport_y=viewport["y"],
                        visible_rows=viewport["rows"],
                        visible_cols=viewport["cols"],
                        margin=1
                    )
                await send_json_safe(ws, {"type": "update", "payload": {"viewport": viewport, "visible": visible}})
                continue  # happy path: next loop

            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                await send_json_safe(ws, {"type": "error", "message": "invalid json"})
                continue

            action = msg.get("action")
            if not action:
                await send_json_safe(ws, {"type": "error", "message": "missing action"})
                continue

            if action != "viewport":
                await send_json_safe(ws, {"type": "error", "message": "unsupported action (only 'viewport' accepted for now)"})
                continue

            # validate and normalize new viewport
            try:
                viewport = validate_and_normalize_viewport(msg.get("viewport", {}))
            except ValueError as exc:
                await send_json_safe(ws, {"type": "error", "message": str(exc)})
                continue

            # ACK message: viewport update successful
            await send_json_safe(ws, {"type": "ok", "message": "viewport updated", "viewport": viewport})

            # Process the next step and send update immediately
            async with game_lock:
                visible = game.step(
                    viewport_x=viewport["x"],
                    viewport_y=viewport["y"],
                    visible_rows=viewport["rows"],
                    visible_cols=viewport["cols"],
                    margin=1
                )
            await send_json_safe(ws, {"type": "update", "payload": {"viewport": viewport, "visible": visible}})

    except WebSocketDisconnect:
        # looger
        print("Client disconnected cleanly")
        return
    except Exception:
        # log/handle other errors; attempt to close socket
        await close_ws_safe(ws)
        raise

