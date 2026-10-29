import asyncio
import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from .config import ICR6_HOST, ICR6_PORT, HTTP_HOST, HTTP_PORT
from .radio import RadioController

app = FastAPI()
radio = RadioController(ICR6_HOST, ICR6_PORT)

connected_websockets = set()

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(radio.poll_status())
    asyncio.create_task(broadcast_loop())

async def broadcast_loop():
    while True:
        if connected_websockets:
            payload = {"type": "radio_state", **radio.state}
            webs = list(connected_websockets)
            for ws in webs:
                try:
                    await ws.send_json(payload)
                except:
                    connected_websockets.discard(ws)
        await asyncio.sleep(0.5)

@app.get("/", response_class=HTMLResponse)
async def get_index():
    web_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "web"))
    index_path = os.path.join(web_dir, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>FreqHub IC-R6 Interface</h1><p>UI files not found.</p>"

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_websockets.add(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            action = data.get("action")
            if action == "set_freq":
                await radio.set_freq(int(data.get("frequencyHz")))
            elif action == "set_mode":
                await radio.set_mode(data.get("mode"))
            elif action == "set_squelch":
                await radio.set_squelch(int(data.get("squelch")))
    except WebSocketDisconnect:
        connected_websockets.discard(websocket)

# 静的ファイルの配信
web_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "web"))
if os.path.exists(web_dir):
    app.mount("/static", StaticFiles(directory=web_dir), name="static")
