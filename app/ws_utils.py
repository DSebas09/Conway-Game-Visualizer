import json
import asyncio
from fastapi import WebSocket, WebSocketDisconnect
from app.utils import validate_and_normalize_viewport


async def send_json_safe(ws: WebSocket, obj: dict) -> bool:
    try:
        await ws.send_text(json.dumps(obj))
        return True
    except Exception:
        # TODO: maybe add a logging: logger.debug(...)
        return False


async def close_ws_safe(ws: WebSocket):
    try:
        await ws.close()
    except Exception:
        pass


async def receive_text_with_timeout(ws: WebSocket, timeout: float | None) -> str | None:
    try:
        return await asyncio.wait_for(ws.receive_text(), timeout=timeout)
    except asyncio.TimeoutError:
        return None
    # WebSocketDisconnect and other exceptions propagate so caller can handle them.


async def wait_for_initial_viewport(ws: WebSocket, initial_timeout: float = 15.0) -> dict[str, int]:
    while True:
        # Wait for client message with a timeout
        raw = await receive_text_with_timeout(ws, timeout=initial_timeout)
        if raw is None:
            raise asyncio.TimeoutError("timeout waiting for initial viewport")

        try:
            msg = json.loads(raw)
        except json.JSONDecodeError:
            await send_json_safe(ws, {"type": "error", "message": "invalid json"})
            continue

        # Verify that the action is 'viewport'
        if msg.get("action") != "viewport":
            await send_json_safe(ws, {"type": "error", "message": "expected first action 'viewport'"})
            continue

        # Validate the payload and normalize if necessary
        try:
            viewport_candidate = msg.get("viewport", {})
            viewport = validate_and_normalize_viewport(viewport_candidate)
            return viewport
        except ValueError as exc:
            await send_json_safe(ws, {"type": "error", "message": str(exc)})
            continue
