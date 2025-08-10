from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from rooms import hub
from settings import settings
from translator import Pipeline
from twilio_bridge import audio_codec
import base64, json

app = FastAPI(title="Interpreter MVP")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from twilio_bridge.twilio_endpoints import router as twilio_router
app.include_router(twilio_router)

pipeline = Pipeline()

@app.get("/")
async def root():
    return {"ok": True}

@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket, room: str = Query("demo"), src: str = Query(settings.default_src), dst: str = Query(settings.default_dst)):
    await ws.accept()
    hub.join(room, ws)
    try:
        while True:
            msg = await ws.receive_text()
            data = json.loads(msg)
            if data.get("type") == "audio":
                pcm = base64.b64decode(data["data"])
                out = pipeline.run(pcm, settings.sample_rate, src, dst)
                await ws.send_json({"type":"subtitle", "src_text": out["src_text"], "dst_text": out["dst_text"]})
                if out["dst_audio"]:
                    b64 = base64.b64encode(out["dst_audio"]).decode("utf-8")
                    await ws.send_json({"type":"tts","dst_text":out["dst_text"],"audio_b64":b64})
    except WebSocketDisconnect:
        hub.leave(room, ws)
