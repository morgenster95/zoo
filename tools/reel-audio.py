"""Zvuk reelu: hlas (macOS `say`), časová osa titulků, hudba a efekty.
  python3 tools/reel-audio.py voice <složka reelu>   → voice.wav, timeline.json (čas každého řádku a slova)
  python3 tools/reel-audio.py mix <složka reelu>     → audio.wav (hlas + hudba + efekty podle events.json)
Potřebuje: macOS (say, afconvert), numpy, ffmpeg (imageio-ffmpeg nebo v PATH, proměnná FFMPEG)."""
import json, os, subprocess, sys, wave
import numpy as np
SR = 44100

def run(cmd): subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def read_wav(path):
    with wave.open(path) as w:
        n = w.getnframes(); ch = w.getnchannels(); raw = w.readframes(n); sw = w.getsampwidth()
        a = np.frombuffer(raw, dtype=np.int16 if sw == 2 else np.int32).astype(np.float32)
        a /= 32768.0 if sw == 2 else 2147483648.0
        if ch > 1: a = a.reshape(-1, ch).mean(1)
        return a, w.getframerate()

def write_wav(path, a, sr=SR):
    a = np.clip(a, -1, 1); pcm = (a * 32767).astype(np.int16)
    with wave.open(path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(pcm.tobytes())

def resample(a, sr):
    if sr == SR: return a
    x = np.linspace(0, len(a) - 1, int(len(a) * SR / sr)); return np.interp(x, np.arange(len(a)), a).astype(np.float32)

def ffmpeg_exe():
    if os.environ.get('FFMPEG'): return os.environ['FFMPEG']
    try:
        import imageio_ffmpeg; return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception: return 'ffmpeg'

def tts_line(text, voice, rate, pitch, mp3):
    """edge-tts: vrací přesné časy slov (WordBoundary); text skriptu se posílá Microsoft službě jako u fronty"""
    import asyncio, edge_tts
    async def go():
        words = []
        comm = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch, boundary='WordBoundary')
        with open(mp3, 'wb') as f:
            async for ch in comm.stream():
                if ch['type'] == 'audio': f.write(ch['data'])
                elif ch['type'] == 'WordBoundary': words.append({'w': ch['text'], 't0': ch['offset'] / 1e7, 't1': (ch['offset'] + ch['duration']) / 1e7})
        return words
    for k in range(4):                                   # služba občas vrátí prázdnou odpověď: pár pokusů
        try: return asyncio.run(go())
        except Exception as e:
            if k == 3: raise
            import time; time.sleep(1.5)

def voice(folder):
    sc = json.load(open(os.path.join(folder, 'script.json')))
    tmp = os.path.join(folder, 'tmp'); os.makedirs(tmp, exist_ok=True)
    t = sc.get('lead', 0.5); lines = []; chunks = []
    for k, ln in enumerate(sc['lines']):
        mp3 = os.path.join(tmp, f'l{k}.mp3'); wavf = os.path.join(tmp, f'l{k}.wav')
        words = tts_line(ln['text'], sc.get('voice', 'en-US-AvaNeural'), sc.get('rate', '+0%'), sc.get('pitch', '+0Hz'), mp3)
        run([ffmpeg_exe(), '-y', '-v', 'error', '-i', mp3, '-ar', str(SR), '-ac', '1', wavf])
        a, sr = read_wav(wavf)
        dur = len(a) / SR
        w0 = words[0]['t0'] if words else 0
        ws = [{'w': w['w'], 't0': round(t + w['t0'] - w0, 3), 't1': round(t + w['t1'] - w0, 3)} for w in words]
        a = a[int(max(0, w0 - 0.05) * SR):]
        dur = len(a) / SR
        lines.append({'id': ln['id'], 'text': ln['text'], 'start': round(t, 3), 'end': round(t + dur, 3), 'words': ws, 'hold': ln.get('hold', 0)})
        chunks.append((t, a))
        t += dur + sc.get('gap', 0.3) + ln.get('hold', 0)
    total = t + sc.get('tail', 2.0)
    out = np.zeros(int(total * SR) + SR, np.float32)
    for st, a in chunks: out[int(st * SR): int(st * SR) + len(a)] += a
    write_wav(os.path.join(folder, 'voice.wav'), out)
    json.dump({'lines': lines, 'total': round(total, 3)}, open(os.path.join(folder, 'timeline.json'), 'w'), indent=1)
    print(f"hlas hotov: {len(lines)} řádků, {total:.1f} s")

# ---------------------------------------------------------------- hudba a efekty (syntéza, jemná: sinusy, dozvuk, žádné čtvercové vlny)
def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)

def bell(f, d, vol=0.2, harm=(1.0, 0.0, 0.28, 0.0, 0.08), decay=5.0):
    n = int(d * SR); tt = np.arange(n) / SR
    w = sum(h * np.sin(2 * np.pi * f * (k + 1) * tt) for k, h in enumerate(harm) if h) * np.exp(-tt * decay)
    a = int(0.004 * SR); w[:a] *= np.linspace(0, 1, a)
    return (w * vol).astype(np.float32)

def pad(f, d, vol=0.05):
    n = int(d * SR); tt = np.arange(n) / SR
    w = (np.sin(2 * np.pi * f * tt) + 0.5 * np.sin(2 * np.pi * f * 1.004 * tt) + 0.25 * np.sin(2 * np.pi * f * 2 * tt)) / 1.75
    e = np.minimum(1, tt / 0.6) * np.minimum(1, (d - tt) / 0.8)
    return (w * e * vol).astype(np.float32)

def echo(a, delay=0.32, gain=0.3, taps=3):
    out = a.copy(); d = int(delay * SR)
    for k in range(1, taps + 1):
        g = gain ** k; out[k * d:] += a[: len(a) - k * d] * g
    return out

def music(total, bpm=108):
    """veselá, lehká hudba: durová smyčka C–G–Am–F, pizzicato basa, „ukulele“ na odbočky, jednoduchá marimba melodie, tichý shaker; krátký dozvuk"""
    beat = 60.0 / bpm; bar = beat * 4
    out = np.zeros(int(total * SR) + 4 * SR, np.float32)
    prog = [(48, [60, 64, 67]), (43, [59, 62, 67]), (45, [57, 60, 64]), (41, [57, 60, 65])]          # C, G, Am, F
    motif = [[76, 79, 81, 79, 76, 74, 72, 74], [79, 83, 86, 83, 79, 78, 74, 78], [81, 84, 88, 84, 81, 79, 76, 79], [77, 81, 84, 81, 79, 77, 74, 77]]
    rng = np.random.RandomState(3)
    t = 0.0; k = 0
    def add(w, st):
        i = int(st * SR); out[i:i + len(w)] += w[: len(out) - i]
    while t < total:
        root, ch = prog[k % 4]
        for b_ in range(4):                                     # poskakující basa: kořen, kvinta
            add(bell(mtof(root - 12 + (7 if b_ % 2 else 0)), 0.35, 0.16, (1.0, 0.0, 0.1), 9), t + b_ * beat)
        for s in range(8):                                      # „ukulele“ akord na odbočky + marimba melodie
            st = t + s * beat / 2
            if s % 2 == 1:
                for m in ch: add(bell(mtof(m), 0.2, 0.035, (1.0, 0.5, 0.25), 18), st)
            if k % 4 != 3 or s < 6:
                add(bell(mtof(motif[k % 4][s] - (12 if k >= 0 else 0)), 0.45, 0.06, (1.0, 0.0, 0.3), 7), st)
            n = int(0.04 * SR); sh = (rng.rand(n) - 0.5) * np.exp(-np.arange(n) / SR * 90) * 0.03; add(sh.astype(np.float32), st)   # shaker
        t += bar; k += 1
    out = echo(out, 0.19, 0.22, 2)
    return out[: int(total * SR) + SR]

def sfx(kind):
    if kind == 'coin':
        return np.concatenate([bell(988, 0.12, 0.12, (1, 0, 0.2), 9), bell(1319, 0.3, 0.12, (1, 0, 0.2), 6)])
    if kind == 'pop':
        d = 0.16; n = int(d * SR); tt = np.arange(n) / SR; f = 520 * np.exp(-tt * 9); w = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 18) * 0.28
        return w.astype(np.float32)
    if kind == 'thunk':
        d = 0.3; n = int(d * SR); tt = np.arange(n) / SR; w = np.sin(2 * np.pi * 80 * tt) * np.exp(-tt * 14) * 0.45
        return w.astype(np.float32)
    if kind == 'tick':
        return bell(620, 0.07, 0.10, (1.0, 0.0, 0.5), 45)       # dřevěné klepnutí
    if kind == 'honk':
        return np.concatenate([bell(392, 0.22, 0.14, (1, 0.4, 0.3), 3.5), np.zeros(int(0.05 * SR), np.float32), bell(494, 0.34, 0.14, (1, 0.4, 0.3), 3.0)])
    if kind == 'spark':
        return np.concatenate([bell(mtof(m), 0.25, 0.07, (1, 0, 0.15), 8) for m in (84, 88, 91)]) if False else sum(np.pad(bell(mtof(m), 0.4, 0.07, (1, 0, 0.15), 7), (int(k * 0.07 * SR), 0))[:int(0.8 * SR)] if False else 0 for k, m in enumerate((84, 88, 91))) or np.concatenate([bell(mtof(84), 0.18, 0.07, (1, 0, 0.15), 8), bell(mtof(88), 0.18, 0.07, (1, 0, 0.15), 8), bell(mtof(91), 0.4, 0.07, (1, 0, 0.15), 6)])
    if kind == 'boing':
        d = 0.4; n = int(d * SR); tt = np.arange(n) / SR; f = 330 + 220 * np.sin(2 * np.pi * 5 * tt) * np.exp(-tt * 4); w = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 5) * 0.2
        return w.astype(np.float32)
    if kind == 'whoosh':
        d = 0.7; n = int(d * SR); r = np.random.RandomState(2).rand(n) - .5; k = np.ones(120) / 120; w = np.convolve(r, k, 'same') * np.hanning(n) * 1.1
        return w.astype(np.float32)
    return np.zeros(10, np.float32)

def mix(folder):
    tl = json.load(open(os.path.join(folder, 'timeline.json'))); total = tl['total']
    ev = json.load(open(os.path.join(folder, 'events.json'))) if os.path.exists(os.path.join(folder, 'events.json')) else []
    voice_a, _ = read_wav(os.path.join(folder, 'voice.wav'))
    out = np.zeros(int(total * SR) + SR, np.float32)
    out += music(total)[: len(out)] * 0.55
    out[: len(voice_a)] += voice_a[: len(out)] * 1.0
    for e in ev:
        w = sfx(e['type']); i = int(e['t'] * SR)
        if i < len(out): out[i:i + len(w)] += w[: len(out) - i]
    # fade out
    n = int(1.0 * SR); out[int(total * SR) - n: int(total * SR)] *= np.linspace(1, 0, n)
    out = out[: int(total * SR)]
    peak = np.abs(out).max(); out = out / max(peak, 1) * 0.9
    write_wav(os.path.join(folder, 'audio.wav'), out)
    print(f'mix hotov: {total:.1f} s, efektů {len(ev)}')

if __name__ == '__main__':
    cmd, folder = sys.argv[1], sys.argv[2]
    {'voice': voice, 'mix': mix}[cmd](folder)
