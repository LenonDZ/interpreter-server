import numpy as np
def pcm16_to_mulaw(pcm16: bytes) -> bytes:
    x = np.frombuffer(pcm16, dtype=np.int16).astype(np.float32)
    x = np.clip(x / 32768.0, -1.0, 1.0)
    mu = 255.0
    y = np.sign(x) * (np.log1p(mu * np.abs(x)) / np.log1p(mu))
    mu_law = ((y + 1) / 2 * 255).astype(np.uint8)
    return mu_law.tobytes()

def mulaw_to_pcm16(mulaw: bytes) -> bytes:
    y = (np.frombuffer(mulaw, dtype=np.uint8).astype(np.float32) / 255.0) * 2 - 1
    mu = 255.0
    x = np.sign(y) * (1.0 / mu) * ((1 + mu) ** np.abs(y) - 1)
    pcm = (x * 32767.0).astype(np.int16)
    return pcm.tobytes()
