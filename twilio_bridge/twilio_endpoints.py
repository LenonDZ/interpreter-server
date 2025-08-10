from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
import os
from twilio.rest import Client

router = APIRouter(prefix="/twilio", tags=["twilio"])

ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN  = os.getenv("TWILIO_AUTH_TOKEN")
TW_NUMBER   = os.getenv("TWILIO_NUMBER")          # +1xxx
PUBLIC_WS   = os.getenv("PUBLIC_WS", "wss://YOUR_ENDPOINT/twilio/ws")
PUBLIC_HTTP = os.getenv("PUBLIC_HTTP", "https://YOUR_ENDPOINT/twilio/voice")

EMERGENCY_PREFIXES = {"999", "112", "911"}

class CallReq(BaseModel):
    user_number: str
    to_number: str
    src_lang: str = "pt"
    dst_lang: str = "en"
    announce_consent: bool = True
    src_voice: str | None = None
    dst_voice: str | None = None

@router.post("/call")
async def start_call(body: CallReq):
    if not (ACCOUNT_SID and AUTH_TOKEN and TW_NUMBER):
        raise HTTPException(status_code=500, detail="Twilio env vars not set.")
    raw = body.to_number.replace(" ", "").replace("-", "")
    if any(raw.endswith(p) or raw.startswith(p) for p in EMERGENCY_PREFIXES):
        raise HTTPException(status_code=400, detail="Emergency numbers not supported.")
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    params = f"&src={body.src_lang}&dst={body.dst_lang}&ac={(1 if body.announce_consent else 0)}"
    if body.src_voice: params += f"&sv={body.src_voice}"
    if body.dst_voice: params += f"&dv={body.dst_voice}"
    twiml_url = f"{PUBLIC_HTTP}?to={body.to_number}{params}"
    call = client.calls.create(to=body.user_number, from_=TW_NUMBER, url=twiml_url)
    return {"sid": call.sid}

@router.post("/voice")
async def voice_webhook(request: Request):
    q = request.query_params
    to  = q.get("to")
    src = q.get("src", "pt")
    dst = q.get("dst", "en")
    ac  = q.get("ac", "1") == "1"
    sv  = q.get("sv")
    consent = (f"""
  <Say language="pt-BR">Aviso: esta ligação está sendo traduzida e pode ser transcrita.</Say>
  <Pause length="0.5"/>
  <Say language="en-US">Notice: this call is being translated and may be transcribed.</Say>
  <Pause length="0.5"/>
""" if ac else "")

    twiml = f"""
<Response>
  {consent}
  <Start>
    <Stream url="{PUBLIC_WS}">
      <Parameter name="role" value="user"/>
      <Parameter name="src" value="{src}"/>
      <Parameter name="dst" value="{dst}"/>
      {"<Parameter name=\"voice\" value=\"%s\"/>" % sv if sv else ""}
    </Stream>
  </Start>
  <Dial>
    <Number url="{PUBLIC_HTTP}/leg?src={dst}&dst={src}&dv={q.get('dv','')}">{to}</Number>
  </Dial>
</Response>
"""
    return PlainTextResponse(twiml, media_type="application/xml")

@router.post("/voice/leg")
async def voice_peer_leg(request: Request):
    q = request.query_params
    src = q.get("src", "en")
    dst = q.get("dst", "pt")
    dv  = q.get("dv")
    twiml = f"""
<Response>
  <Start>
    <Stream url="{PUBLIC_WS}">
      <Parameter name="role" value="peer"/>
      <Parameter name="src" value="{src}"/>
      <Parameter name="dst" value="{dst}"/>
      {"<Parameter name=\"voice\" value=\"%s\"/>" % dv if dv else ""}
    </Stream>
  </Start>
</Response>
"""
    return PlainTextResponse(twiml, media_type="application/xml")
