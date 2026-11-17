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

def voice(folder):
    sc = json.load(open(os.path.join(folder, 'script.json')))
    tmp = os.path.join(folder, 'tmp'); os.makedirs(tmp, exist_ok=True)
    t = sc.get('lead', 0.5); lines = []; chunks = []
    for k, ln in enumerate(sc['lines']):
        aiff = os.path.join(tmp, f'l{k}.aiff'); wavf = os.path.join(tmp, f'l{k}.wav')
        run(['say', '-v', sc.get('voice', 'Samantha'), '-r', str(sc.get('rate', 175)), '-o', aiff, ln['text']])
        run(['afconvert', '-f', 'WAVE', '-d', f'LEI16@{SR}', '-c', '1', aiff, wavf])
        a, sr = read_wav(wavf)
        # ořez ticha na začátku a na konci
        nz = np.where(np.abs(a) > 0.01)[0]
        if len(nz): a = a[max(0, nz[0] - 200): nz[-1] + 400]
        dur = len(a) / SR
        words = ln['text'].replace(',', '').replace('.', '').split()
        lens = np.array([len(w) + 2 for w in words], float); cum = np.concatenate([[0], np.cumsum(lens)]) / lens.sum()
        ws = [{'w': w, 't0': round(t + cum[i] * dur, 3), 't1': round(t + cum[i + 1] * dur, 3)} for i, w in enumerate(words)]
        lines.append({'id': ln['id'], 'text': ln['text'], 'start': round(t, 3), 'end': round(t + dur, 3), 'words': ws, 'hold': ln.get('hold', 0)})
        chunks.append((t, a))
        t += dur + sc.get('gap', 0.3) + ln.get('hold', 0)
    total = t + sc.get('tail', 2.0)
    out = np.zeros(int(total * SR) + SR, np.float32)
    for st, a in chunks: out[int(st * SR): int(st * SR) + len(a)] += a
    write_wav(os.path.join(folder, 'voice.wav'), out)
    json.dump({'lines': lines, 'total': round(total, 3)}, open(os.path.join(folder, 'timeline.json'), 'w'), indent=1)
    print(f"hlas hotov: {len(lines)} řádků, {total:.1f} s")

# ---------------------------------------------------------------- hudba a efekty (syntéza)
def sq(f, d, duty=0.5, sr=SR):
    t = np.arange(int(d * sr)) / sr; ph = (t * f) % 1.0; return np.where(ph < duty, 1.0, -1.0).astype(np.float32)
def tri(f, d, sr=SR):
    t = np.arange(int(d * sr)) / sr; ph = (t * f) % 1.0; return (4 * np.abs(ph - 0.5) - 1).astype(np.float32)
def env(n, a=0.005, r=0.1, sr=SR):
    e = np.ones(n, np.float32); na = int(a * sr); nr = int(r * sr)
    if na: e[:na] = np.linspace(0, 1, na)
    if nr: e[-nr:] *= np.linspace(1, 0, min(nr, n))
    return e
def note(f, d, kind='sq', vol=0.3, duty=0.5):
    w = sq(f, d, duty) if kind == 'sq' else tri(f, d); return w * env(len(w), 0.004, min(d * 0.6, 0.18)) * vol
def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)

def music(total, bpm=116):
    beat = 60.0 / bpm; out = np.zeros(int(total * SR) + SR, np.float32)
    prog = [(48, [60, 64, 67]), (45, [57, 60, 64]), (41, [57, 60, 65]), (43, [55, 59, 62])]   # C Am F G
    bar = beat * 4; t = 0.0; k = 0
    while t < total:
        root, ch = prog[k % 4]
        for s in range(8):                               # arpeggio osminy
            n = mtof(ch[s % 3] + (12 if s % 4 == 3 else 0)); st = t + s * beat / 2
            w = note(n, beat / 2 * 0.9, 'sq', 0.07, 0.25); i = int(st * SR); out[i:i + len(w)] += w[: len(out) - i]
        for b in range(2):                               # basa
            w = note(mtof(root - 12 + (7 if b else 0)), beat * 1.8, 'tri', 0.18); i = int((t + b * 2 * beat) * SR); out[i:i + len(w)] += w[: len(out) - i]
        t += bar; k += 1
    return out

def sfx(kind):
    if kind == 'coin':
        return np.concatenate([note(988, 0.07, 'sq', 0.22, 0.5), note(1319, 0.16, 'sq', 0.22, 0.5)])
    if kind == 'pop':
        d = 0.14; n = int(d * SR); t = np.arange(n) / SR; f = 700 * np.exp(-t * 14); w = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.002, 0.1) * 0.35
        return w.astype(np.float32)
    if kind == 'thunk':
        d = 0.16; n = int(d * SR); t = np.arange(n) / SR; w = np.sin(2 * np.pi * 95 * t) * np.exp(-t * 22) * 0.6 + (np.random.RandomState(1).rand(n) - .5) * np.exp(-t * 60) * 0.3
        return w.astype(np.float32)
    if kind == 'tick':
        return note(1500, 0.03, 'sq', 0.16, 0.25)
    if kind == 'honk':
        return np.concatenate([note(330, 0.16, 'sq', 0.26, 0.5), np.zeros(int(0.04 * SR), np.float32), note(392, 0.22, 'sq', 0.26, 0.5)])
    if kind == 'spark':
        return np.concatenate([note(mtof(m), 0.07, 'sq', 0.14, 0.25) for m in (84, 88, 91, 96)])
    if kind == 'boing':
        d = 0.35; n = int(d * SR); t = np.arange(n) / SR; f = 300 + 250 * np.sin(2 * np.pi * 6 * t) * np.exp(-t * 5); w = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * env(n, 0.005, 0.2) * 0.22
        return w.astype(np.float32)
    if kind == 'whoosh':
        d = 0.5; n = int(d * SR); r = np.random.RandomState(2).rand(n) - .5; k = np.ones(40) / 40; w = np.convolve(r, k, 'same') * np.hanning(n) * 1.4
        return w.astype(np.float32)
    return np.zeros(10, np.float32)

def mix(folder):
    tl = json.load(open(os.path.join(folder, 'timeline.json'))); total = tl['total']
    ev = json.load(open(os.path.join(folder, 'events.json'))) if os.path.exists(os.path.join(folder, 'events.json')) else []
    voice_a, _ = read_wav(os.path.join(folder, 'voice.wav'))
    out = np.zeros(int(total * SR) + SR, np.float32)
    out += music(total)[: len(out)]
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
