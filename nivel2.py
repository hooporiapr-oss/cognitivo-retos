# "¿Quién tiene el balón? Nivel 2" — the same game as quien.py with three
# identical balls. Follow the one that starts with #7.
#   python3 nivel2.py reto preview|render       -> nivel2-video.mp4 (silent)
#   python3 nivel2.py respuesta preview|render  -> nivel2-respuesta-video.mp4
import sys, os, math, json, random, subprocess
from PIL import Image, ImageDraw, ImageFilter
import sigue as G

W, H, FPS = G.W, G.H, G.FPS
# ── the five players: top of the key, two wings, two low posts ──
SPOTS = [(540, 680), (190, 1135), (890, 1135), (300, 1565), (780, 1565)]   # #7 in the centre circle, like challenge 1's top ball
NUMS = ['7', '3', '11', '14', '21']
TR = 80                                           # token radius
HAND = (60, -60)                                  # where a held ball sits on the token
BR = 0.80                                         # ball size vs challenge 1

# ── the passes: never straight back, never across another player ──
def cerca(p, q, r):
    (x1, y1), (x2, y2), (x0, y0) = p, q, r
    dx, dy = x2 - x1, y2 - y1; L2 = dx * dx + dy * dy
    u = max(0, min(1, ((x0 - x1) * dx + (y0 - y1) * dy) / L2))
    return math.hypot(x1 + u * dx - x0, y1 + u * dy - y0)
OK = {(i, j) for i in range(5) for j in range(5) if i != j and
      all(cerca(SPOTS[i], SPOTS[j], SPOTS[k]) > 150 for k in range(5) if k not in (i, j))}
# Nivel 2: three identical balls. The one to follow (ball 0) starts with
# #7 and is passed alone three times; a second ball comes in, then a third.
# With three balls only two players are free, so each beat moves one or two
# balls, never three — nobody ever holds two balls at once.
SOLO = [0.82, 0.76, 0.70]
DOBLE = [0.66, 0.62, 0.58, 0.55]
TRIPLE = [0.60, 0.57, 0.54, 0.51, 0.48, 0.46, 0.44, 0.42, 0.40, 0.38, 0.37, 0.36]
SEED = 10
def plan(seed):
    rnd = random.Random(seed)
    h, prev, beats, entradas = [0], [None], [], []
    def libres(): return [j for j in range(5) if j not in h]
    def paso(cuantos):
        for _ in range(400):
            mueven = rnd.sample(range(len(h)), cuantos); usados = set(); mv = {}
            for k in mueven:
                op = [j for j in libres() if (h[k], j) in OK and j != prev[k] and j not in usados]
                if not op: break
                j = rnd.choice(op); usados.add(j); mv[k] = (h[k], j)
            else:
                for k, (i, j) in mv.items(): prev[k] = i; h[k] = j
                return mv
        raise RuntimeError('no beat')
    for d in SOLO: beats.append((d, paso(1)))
    for d_list, n in ((DOBLE, 2), (TRIPLE, 3)):
        r = rnd.choice(libres()); entradas.append((len(beats), r)); h.append(r); prev.append(None)
        for k, d in enumerate(d_list):
            cuantos = 1 if (n == 2 and k == 2) or (n == 3 and k in (2, 7)) else 2
            beats.append((d, paso(cuantos)))
    return beats, entradas, list(h)
PASES, ENTRADAS, FINALES = plan(SEED)
FINAL = FINALES[0]                               # who ends with the ball to follow
NB = len(FINALES)

T_SHOW, T_HIDE = 0.5, 2.7
t, PASS_T, T_IN = 3.1, [], []                     # T_IN: (start, end, ball, receiver, from)
for k, (d, mv) in enumerate(PASES):
    for (kb, r) in ENTRADAS:
        if kb == k:
            x0 = -120 if SPOTS[r][0] < 540 else W + 120
            T_IN.append((t, t + 0.7, len(T_IN) + 1, r, (x0, SPOTS[r][1] - 60))); t += 0.85
    PASS_T.append((t, t + d)); t += d + max(0.07, 0.17 - 0.006 * k)
T_STOP = PASS_T[-1][1]
T_ASK = T_STOP + 0.55
T_BRAND = T_ASK + 4.6
DUR = T_BRAND + 2.4

def mano(i): return (SPOTS[i][0] + HAND[0], SPOTS[i][1] + HAND[1])

def vuelo(p, q, u, lado=1):
    u = u * u * (3 - 2 * u)
    mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
    dx, dy = q[0] - p[0], q[1] - p[1]; L = math.hypot(dx, dy) or 1
    cx, cy = mx - dy / L * 0.12 * L * lado, my + dx / L * 0.12 * L * lado
    x = (1 - u) ** 2 * p[0] + 2 * (1 - u) * u * cx + u * u * q[0]
    y = (1 - u) ** 2 * p[1] + 2 * (1 - u) * u * cy + u * u * q[1]
    return x, y, 1 + 0.22 * math.sin(u * math.pi)

def balon(g, cual=0):
    """(x, y, scale, visible) of ball cual (0 is the one to follow) at game time g"""
    h = 0
    if cual:
        a, b, _, r, desde = T_IN[cual - 1]
        if g < a: return 0, 0, 1, False
        if g < b: x, y, sc = vuelo(desde, mano(r), (g - a) / (b - a)); return x, y, sc, True
        h = r
    for (a, b), (d, mv) in zip(PASS_T, PASES):
        if g < a: break
        if cual not in mv: continue
        i, j = mv[cual]
        if g < b: x, y, sc = vuelo(mano(i), mano(j), (g - a) / (b - a)); return x, y, sc, True
        h = j
    x, y = mano(h); return x, y, 1.0, True

# ── the player tokens ──
def token(num, hot=False, dim=1.0):
    s = 2 * (TR + 60); im = Image.new('RGBA', (s, s), (0, 0, 0, 0)); c = s / 2
    ring = (255, 70, 70) if hot else G.CG_GOLD
    gl = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    ImageDraw.Draw(gl).ellipse((c - TR - 8, c - TR - 8, c + TR + 8, c + TR + 8), fill=ring + (int(170 * dim),))
    im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(16)))
    d = ImageDraw.Draw(im)
    d.ellipse((c - TR, c - TR, c + TR, c + TR), fill=(255, 70, 70, 255) if hot else (22, 20, 28, 255), outline=ring + (255,), width=8)
    d.text((c, c + 4), num, font=G.bebas(104), fill=(255, 255, 255, 255), anchor='mm')
    if dim < 1: im.putalpha(im.getchannel('A').point(lambda v: int(v * (0.35 + 0.65 * dim))))
    return im
TOK = [token(n) for n in NUMS]; TOK_DIM = [token(n, dim=0.0) for n in NUMS]; TOK_HOT = [token(n, True) for n in NUMS]

def jugadores(img, tt, hot=None, dim=False, intro=True):
    for k, (x, y) in enumerate(SPOTS):
        a = G.ease((tt - 0.1 - 0.07 * k) / 0.3) if intro else 1
        if a <= 0: continue
        spr = TOK_HOT[k] if k == hot else TOK_DIM[k] if dim else TOK[k]
        sc = (0.6 + 0.4 * a) * (G.pop((tt - T_REVEAL_R) / 0.4) if (k == hot and MODO == 'respuesta') else 1)
        G.paste_c(img, spr, x, y, a, sc)

def pelota(img, x, y, sc, hot=False):
    G.paste_c(img, G.BALL_HOT if hot else G.BALL, x, y, 1.0, BR * sc)

def caja(img, u, l1, l2, borde):
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    ld.rounded_rectangle((90, 1700, 990, 1890), radius=26, fill=G.CG_DARK + (238,), outline=borde + (255,), width=4)
    G.text_c(ld, (540, 1760), l1, G.bebas(96), G.WHITE)
    G.text_c(ld, (540, 1848), l2, G.outfit(48), G.CG_GOLD)
    lay.putalpha(lay.getchannel('A').point(lambda v: int(v * u))); img.alpha_composite(lay)

def apagon(img, u):
    img.alpha_composite(Image.new('RGBA', (W, H), (4, 4, 8, int(225 * u))))

# ── the challenge ──
def frame_reto(tt):
    img = G.BG.copy().convert('RGBA')
    # the lights flicker on the last passes, then go out on the last catch
    flick = any(abs(tt - (PASS_T[k][0] + 0.12)) < 0.05 for k in (-3, -2))
    if flick: apagon(img, 0.55)
    if tt >= T_STOP: apagon(img, G.ease((tt - T_STOP) / 0.08))
    if tt < T_BRAND: G.wordmark(img)
    G.title(img, G.ease(tt / 0.3), '¿QUIÉN TIENE', 'EL ', 'BALÓN?')
    jugadores(img, tt, dim=tt >= T_STOP)
    if tt < T_STOP:
        for k in range(1, NB):
            x, y, sc, v = balon(tt, k)
            if v: pelota(img, x, y, sc)
        x, y, sc, _ = balon(tt)
        if tt > 0.35: pelota(img, x, y, sc * G.ease((tt - 0.35) / 0.25), hot=T_SHOW <= tt < T_HIDE)
    if T_SHOW <= tt < T_HIDE:                     # where it starts
        x, y = mano(0); ph = tt - T_SHOW; rr = 62 * BR + 16 + 7 * math.sin(ph * 7)
        ImageDraw.Draw(img).ellipse((x - rr, y - rr, x + rr, y + rr), outline=G.RED, width=7)
        a = G.ease(ph / 0.3) * (1 - G.ease((tt - (T_HIDE - 0.3)) / 0.3))
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        ld.rounded_rectangle((x + 80, y - 44, x + 420, y + 44), radius=44, fill=(255, 70, 70, 235))
        ld.polygon([(x + 64, y), (x + 88, y - 18), (x + 88, y + 18)], fill=(255, 70, 70, 235))
        G.text_c(ld, (x + 250, y + 2), 'EMPIEZA AQUÍ', G.outfit(42, 800), G.WHITE)
        lay.putalpha(lay.getchannel('A').point(lambda v: int(v * a))); img.alpha_composite(lay)
        G.bottom(img, 'Nivel 2 · Sigue este balón', G.ease(ph / 0.3), size=56)
    elif T_HIDE <= tt < T_IN[0][0] - 0.2:
        G.bottom(img, '¡No lo pierdas!', G.ease((tt - T_HIDE) / 0.25), G.CG_GOLD)
    elif any(e[0] - 0.2 <= tt < e[1] + 1.2 for e in T_IN):
        e = [e for e in T_IN if e[0] - 0.2 <= tt < e[1] + 1.2][0]
        G.bottom(img, '¡Entra otro balón!' if e[2] == 1 else '¡Y otro más!', G.ease((tt - e[0] + 0.2) / 0.25), G.CG_ORANGE, 66)
    elif tt < T_IN[0][0]:
        G.bottom(img, 'Concéntrate...')
    elif tt < (T_IN[-1][1] + T_STOP) / 2:
        G.bottom(img, 'Concéntrate...')
    elif tt < T_STOP:
        G.bottom(img, '¡Más rápido!', 1.0, G.CG_ORANGE)
    elif tt < T_ASK:
        G.bottom(img, '¡Se fue la luz!', G.ease((tt - T_STOP) / 0.15), G.CG_GOLD, 66)
    if T_ASK <= tt < T_BRAND:
        u = G.ease((tt - T_ASK) / 0.35)
        caja(img, u, '¿QUIÉN TIENE EL BALÓN?', 'El que empezó con el 7 · Comenta el número', G.CG_GOLD)
        left = max(0, 1 - (tt - T_ASK - 0.4) / (T_BRAND - T_ASK - 0.6))
        ImageDraw.Draw(img).rounded_rectangle((120, 1682, 120 + 840 * left, 1692), radius=5, fill=G.CG_ORANGE)
    if tt >= T_BRAND:
        G.endcard(img, G.ease((tt - T_BRAND) / 0.4), '¿Lo viste? Comenta el número')
    return img.convert('RGB')

# ── the answer: the same passes in slow motion, with a trail and a count ──
SLOW = 0.68
T0 = 1.8
G0 = PASS_T[0][0]
def g_of(tt): return G0 - 0.01 if tt < T0 else G0 + (tt - T0) * SLOW
T_STOP_R = T0 + (T_STOP - G0) / SLOW
T_ROLL_R = T_STOP_R + 0.3
T_REVEAL_R = T_ROLL_R + 1.3
T_BRAND_R = T_REVEAL_R + 3.2
DUR_R = T_BRAND_R + 2.4

def frame_resp(tt):
    img = G.BG.copy().convert('RGBA')
    if tt < T_BRAND_R: G.wordmark(img)
    G.title(img, G.ease(tt / 0.3), '¿LO SEGUISTE?', 'MÍRALO ', 'OTRA VEZ')
    g = min(g_of(tt), T_STOP)
    hot = FINAL if tt >= T_REVEAL_R else None
    jugadores(img, tt, hot=hot, intro=False)
    if T0 <= tt < T_REVEAL_R:
        for i in range(12, 0, -1):                 # the trail
            x, y, _, _ = balon(max(G0, g - i * 0.03)); r = 22 - i * 1.4
            tl = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(tl).ellipse((x - r, y - r, x + r, y + r), fill=(255, 70, 70, int(140 * (1 - i / 13))))
            img.alpha_composite(tl)
    if tt < T_REVEAL_R:
        for k in range(1, NB):
            x, y, sc, v = balon(g, k)
            if v: G.paste_c(img, G.BALL, x, y, 0.45, BR * sc)            # the other balls, faded
        x, y, sc, _ = balon(g); pelota(img, x, y, sc, hot=True)        # at the reveal the player's number is what counts
    hechos = sum(1 for (a, b), p in zip(PASS_T, PASES) if 0 in p[1] and g >= b - 1e-6)
    total = sum(1 for p in PASES if 0 in p[1])
    if tt < T0:
        G.bottom(img, 'Empieza con el 7', G.ease((tt - 0.2) / 0.3))
    elif tt < T_STOP_R + 0.05:
        G.bottom(img, 'Sigue el rojo · pase %d de %d' % (max(1, min(total, hechos + 1)), total), 1.0, G.CG_GOLD, 56)
    elif tt < T_REVEAL_R:
        G.bottom(img, 'Lo tiene...', G.ease((tt - T_ROLL_R) / 0.25), G.WHITE, 66)
    if T_REVEAL_R <= tt < T_BRAND_R:
        sc = G.pop((tt - T_REVEAL_R) / 0.4)
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay); u = G.ease((tt - T_REVEAL_R) / 0.3)
        ld.rounded_rectangle((90, 1700, 990, 1890), radius=26, fill=G.CG_DARK + (238,), outline=(255, 70, 70, 255), width=4)
        G.text_c(ld, (540, 1762), '¡ERA EL ' + NUMS[FINAL] + '!', G.bebas(int(118 * sc)), G.WHITE)
        G.text_c(ld, (540, 1850), '¿Acertaste? Cuéntanos', G.outfit(48), G.CG_GOLD)
        lay.putalpha(lay.getchannel('A').point(lambda v: int(v * u))); img.alpha_composite(lay)
    if tt >= T_BRAND_R:
        G.endcard(img, G.ease((tt - T_BRAND_R) / 0.4), 'Un reto nuevo cada semana')
    return img.convert('RGB')

def render(fn, dur, out):
    tmp = out.replace('.mp4', '.tmp.mp4')
    p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '%dx%d' % (W, H), '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', tmp], stdin=subprocess.PIPE)
    for i in range(int(dur * FPS)): p.stdin.write(fn(i / FPS).tobytes())
    p.stdin.close(); p.wait()
    if p.returncode == 0: os.replace(tmp, out)
    print('done', p.returncode)

MODO = 'reto'
if __name__ == '__main__':
    MODO = sys.argv[1]; acc = sys.argv[2] if len(sys.argv) > 2 else 'preview'
    G.BG = G.background()
    if MODO == 'reto':
        info = {'duration': round(DUR, 2), 't_show': T_SHOW, 't_hide': T_HIDE, 't_stop': round(T_STOP, 3), 't_ask': round(T_ASK, 3),
                't_brand': round(T_BRAND, 3), 'swap_times': [(round(a, 3), round(b, 3)) for a, b in [e[:2] for e in T_IN] + PASS_T], 'answer': NUMS[FINAL]}
        json.dump(info, open('info-quien-nivel-2.json', 'w')); print(info['duration'], 'answer', NUMS[FINAL], 'others', [NUMS[f] for f in FINALES[1:]])
        if acc == 'preview':
            for tt in [1.2, 6.0, T_STOP + 0.3, T_ASK + 1.5]: frame_reto(tt).save('n-%05.2f.png' % tt)
        else: render(frame_reto, DUR, 'nivel2-video.mp4')
    else:
        info = {'duration': round(DUR_R, 2), 't_show': 0.0, 't_hide': T0, 't_stop': round(T_STOP_R, 3), 't_ask': round(T_ROLL_R, 3),
                't_reveal': round(T_REVEAL_R, 3), 't_brand': round(T_BRAND_R, 3),
                'swap_times': [(round(T0 + (a - G0) / SLOW, 3), round(T0 + (b - G0) / SLOW, 3)) for a, b in PASS_T]}
        json.dump(info, open('info-quien-nivel-2-respuesta.json', 'w')); print(info['duration'], 'answer', NUMS[FINAL])
        if acc == 'preview':
            for tt in [0.8, 6.0, T_REVEAL_R + 0.8]: frame_resp(tt).save('nr-%05.2f.png' % tt)
        else: render(frame_resp, DUR_R, 'nivel2-respuesta-video.mp4')
