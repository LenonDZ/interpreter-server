import os
from pydantic import BaseModel

class Settings(BaseModel):
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    provider_asr: str = os.getenv("PROVIDER_ASR", "dummy")   # whisper | dummy
    provider_mt: str = os.getenv("PROVIDER_MT", "dummy")     # argos | dummy
    provider_tts: str = os.getenv("PROVIDER_TTS", "dummy")   # coqui | dummy
    default_src: str = os.getenv("DEFAULT_SRC", "pt")
    default_dst: str = os.getenv("DEFAULT_DST", "en")
    sample_rate: int = int(os.getenv("SAMPLE_RATE", "16000"))

settings = Settings()
