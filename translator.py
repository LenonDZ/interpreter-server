from settings import settings
import numpy as np

class ASR:
    def __init__(self):
        self.kind = settings.provider_asr
        if self.kind == "whisper":
            try:
                from faster_whisper import WhisperModel
                self.model = WhisperModel("small", device="cpu", compute_type="int8")
            except Exception:
                self.kind = "dummy"

    def transcribe(self, pcm16: bytes, sr: int):
        if self.kind == "whisper":
            audio = np.frombuffer(pcm16, dtype=np.int16).astype(np.float32) / 32768.0
            segments, _ = self.model.transcribe(audio, language=None, task="transcribe")
            text = " ".join([s.text for s in segments])
            return text.strip()
        return ""

class MT:
    def __init__(self):
        self.kind = settings.provider_mt
        if self.kind == "argos":
            try:
                import argostranslate.translate # noqa
                self.ok = True
            except Exception:
                self.kind = "dummy"

    def translate(self, text: str, src: str, dst: str) -> str:
        if not text:
            return text
        if self.kind == "argos":
            try:
                import argostranslate.translate as t
                return t.translate(text, src, dst)
            except Exception:
                pass
        return f"[{src}->{dst}] {text}"

class TTS:
    def __init__(self):
        self.kind = settings.provider_tts
        if self.kind == "coqui":
            try:
                from TTS.api import TTS as CoquiTTS
                self.tts = CoquiTTS(model_name="tts_models/multilingual/multi-dataset/your_tts")
            except Exception:
                self.kind = "dummy"

    def synth(self, text: str, sr: int, voice: str | None = None) -> bytes:
        if not text:
            return b""
        if self.kind == "coqui":
            wav = self.tts.tts(text)
            wav = (np.array(wav) * 32767.0).astype(np.int16).tobytes()
            return wav
        return b""

class Pipeline:
    def __init__(self):
        self.asr = ASR()
        self.mt  = MT()
        self.tts = TTS()

    def run(self, pcm16: bytes, sr: int, src: str, dst: str, voice: str | None = None):
        text_src = self.asr.transcribe(pcm16, sr)
        text_dst = self.mt.translate(text_src, src, dst)
        wav_tts  = self.tts.synth(text_dst, sr, voice=voice)
        return {"src_text": text_src, "dst_text": text_dst, "dst_audio": wav_tts}
