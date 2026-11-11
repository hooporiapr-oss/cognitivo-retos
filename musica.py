# Music for "¿Puedes seguir el balón?": a tense 120 BPM pulse, a whoosh on
# every swap, a sting when the target is shown, a drum roll under the
# question, a hit at the end card.
import json, numpy as np, scipy.io.wavfile as wf
SR = 44100
import sys
INFO = sys.argv[1] if len(sys.argv) > 1 else 'info.json'; WAV = sys.argv[2] if len(sys.argv) > 2 else 'musica.wav'
I = json.load(open(INFO)); D = I['duration']
n = int(D * SR); out = np.zeros((n, 2), np.float32)
t = np.arange(n) / SR
rng = np.random.default_rng(3)
def add(sig, at, gain=1.0, pan=0.0):
    i = int(at * SR); j = min(n, i + len(sig))
    if i >= n: return
    s = sig[:j - i] * gain
    out[i:j, 0] += s * (1 - max(0, pan)); out[i:j, 1] += s * (1 + min(0, pan))
def env(L, a=0.005, r=0.2):
    e = np.ones(L); A = int(a * SR); R = int(r * SR)
    e[:A] = np.linspace(0, 1, A); e[-R:] *= np.linspace(1, 0, R) if R < L else 1; return e
def kick():
    L = int(0.32 * SR); tt = np.arange(L) / SR; f = 50 + 90 * np.exp(-tt * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 9)
def hat():
    L = int(0.05 * SR); x = rng.standard_normal(L); x = np.diff(np.concatenate([[0], x])); return x * np.exp(-np.arange(L) / SR * 80) * 0.5
def snare():
    L = int(0.18 * SR); tt = np.arange(L) / SR
    return (rng.standard_normal(L) * 0.7 + np.sin(2 * np.pi * 190 * tt) * 0.5) * np.exp(-tt * 22)
def tone(f, L, kind='sin'):
    tt = np.arange(int(L * SR)) / SR
    if kind == 'saw': x = 2 * ((tt * f) % 1) - 1
    else: x = np.sin(2 * np.pi * f * tt)
    return x
def whoosh(L):
    m = int(L * SR); x = rng.standard_normal(m)
    # sweep a simple one-pole lowpass up and down
    c = 0.02 + 0.5 * np.sin(np.linspace(0, np.pi, m)) ** 2; y = np.zeros(m); z = 0
    for k in range(m): z += c[k] * (x[k] - z); y[k] = z
    return y * np.sin(np.linspace(0, np.pi, m)) ** 1.5 * 1.4
beat = 0.5
end_music = I['t_brand']
# pulse bed: A minor, bass on every beat, hats on eighths, a pad
k = 0; tb = 0.0
while tb < end_music:
    add(kick(), tb, 0.9)
    add(hat(), tb + beat / 2, 0.35, 0.3)
    if tb >= I['t_hide'] and int(round(tb / beat)) % 2 == 1: add(snare(), tb, 0.35)
    bassf = [55, 55, 65.4, 49][int(tb / 2) % 4]
    b = tone(bassf, beat * 0.9, 'saw'); b = np.convolve(b, np.ones(40) / 40, 'same') * env(len(b), 0.01, 0.15)
    add(b, tb, 0.28)
    tb += beat
pad = sum(tone(f, end_music) for f in [220, 261.6, 329.6]) / 3
pad *= np.minimum(1, np.arange(len(pad)) / SR / 2) * 0.10
add(pad, 0)
# ticking clock that speeds up with the swaps
for a, b in I.get('swap_times', []):
    add(whoosh(b - a), a, 0.45, rng.uniform(-0.5, 0.5))
    tk = tone(2200, 0.03) * np.exp(-np.arange(int(0.03 * SR)) / SR * 120); add(tk, a, 0.25)
# The Fortress: each target sounds its own note when it lights up
for at, f in I.get('flashes', []):
    m = int(0.5 * SR); tt = np.arange(m) / SR
    bell = (np.sin(2 * np.pi * f * tt) + 0.4 * np.sin(2 * np.pi * 2 * f * tt) + 0.15 * np.sin(2 * np.pi * 3 * f * tt)) * np.exp(-tt * 6)
    add(bell, at, 0.55)
# target sting
st = sum(tone(f, 0.9) for f in [659, 880, 1318]) / 3 * np.exp(-np.arange(int(0.9 * SR)) / SR * 4)
add(st, I['t_show'], 0.45)
# stop + question: a riser then a drum roll
add(kick() * 1.4, I['t_stop'], 1.0)
roll_t = I['t_ask'] if I.get('roll', True) else 1e9; dt = 0.11
ROLL_END = I.get('t_reveal', I['t_brand'])
while roll_t < ROLL_END - 0.1:
    add(snare(), roll_t, 0.12 + 0.35 * (roll_t - I['t_ask']) / (ROLL_END - I['t_ask']), rng.uniform(-0.2, 0.2))
    dt = max(0.045, dt * 0.97); roll_t += dt
# the answer: a hit and a bright chord
if 't_reveal' in I:
    add(kick() * 1.5, I['t_reveal'], 1.0)
    add(sum(tone(f, 1.6) for f in [523, 659, 784, 1046]) / 4 * np.exp(-np.arange(int(1.6 * SR)) / SR * 2.2), I['t_reveal'], 0.6)
# end hit
hit = kick() * 1.6; add(hit, I['t_brand'], 1.0)
cr = rng.standard_normal(int(1.6 * SR)) * np.exp(-np.arange(int(1.6 * SR)) / SR * 3) * 0.4
add(cr, I['t_brand'], 0.5)
ch = sum(tone(f, 2.0) for f in [440, 554, 659, 880]) / 4 * np.exp(-np.arange(int(2.0 * SR)) / SR * 1.6)
add(ch, I['t_brand'], 0.5)
out /= np.max(np.abs(out)) / 0.89
fade = int(0.4 * SR); out[-fade:] *= np.linspace(1, 0, fade)[:, None]
wf.write(WAV, SR, (out * 32767).astype(np.int16))
print('ok', D)
