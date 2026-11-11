# Challenge 2 · ¿Puedes recordar el orden?  (The Fortress)
# The real Fortress board: a 5x5 court with five targets in a 2-1-2 —
# the four corners and the centre, each in its colour. A chain of six
# lights up; then the question: which colour lit up 4th?
#   python3 fortress.py reto|respuesta preview|render
import sys, os, math, json, subprocess
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
import sigue as G

W, H, FPS = 1080, 1920, 30
COL = {12: ((255, 215, 0), 'DORADO'), 0: ((255, 107, 53), 'NARANJA'), 4: ((255, 20, 147), 'ROSA'),
       20: ((0, 217, 217), 'CIAN'), 24: ((155, 89, 182), 'MORADO')}
PITCH = {12: 523, 0: 440, 4: 659, 20: 392, 24: 587}
CHAIN = [12, 0, 24, 4, 20, 0]                    # the 4th is ROSA
ASK = 3                                           # 0-based: the 4th

BX, BY, BS = 120, 560, 840                        # the court on screen
PAD = 46; CELL = (BS - 2 * PAD) / 5

def cell_box(i, grow=0):
    r, c = divmod(i, 5)
    x0 = BX + PAD + c * CELL + 7 - grow; y0 = BY + PAD + r * CELL + 7 - grow
    return (x0, y0, x0 + CELL - 14 + 2 * grow, y0 + CELL - 14 + 2 * grow)
def cell_center(i):
    b = cell_box(i); return ((b[0] + b[2]) / 2, (b[1] + b[3]) / 2)

def background():
    g = np.zeros((H, W, 3), np.float32)
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(-1, 1, W)[None, :]
    for c, (a, b) in enumerate([(16, 8), (14, 10), (40, 24)]): g[..., c] = a * (1 - yy) + b * yy
    glow = np.exp(-(xx ** 2 * 2.2 + ((yy - 0.5) * 2.4) ** 2)); g += glow[..., None] * np.array([60, 44, 20])
    img = Image.fromarray(np.clip(g, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(img); import random; rnd = random.Random(9)
    for _ in range(120):
        x, y = rnd.randrange(W), rnd.randrange(H); r = rnd.choice([1, 1, 2]); a = rnd.randrange(60, 160)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(a, a, a + 15))
    # the hardwood court
    court = Image.new('RGB', (BS, BS)); cd = ImageDraw.Draw(court)
    for x in range(BS):
        k = (x // 76) % 3; base = [(138, 82, 40), (128, 74, 34), (146, 88, 44)][k]
        sh = int(10 * math.sin(x * 0.9) * (x % 76 < 2))
        cd.line((x, 0, x, BS), fill=(base[0] - sh, base[1] - sh, base[2] - sh))
    for x in range(0, BS, 76): cd.line((x, 0, x, BS), fill=(90, 50, 22), width=2)
    vign = Image.new('L', (BS, BS), 0); ImageDraw.Draw(vign).ellipse((-200, -260, BS + 200, BS + 160), fill=90)
    court = Image.composite(Image.new('RGB', (BS, BS), (190, 120, 70)), court, vign.filter(ImageFilter.GaussianBlur(120)).point(lambda v: v // 3))
    cd = ImageDraw.Draw(court); L = (255, 255, 255); w = 6; m = 18
    cd.rectangle((m, m, BS - m, BS - m), outline=L, width=w)
    kw = BS * 0.32; cd.rectangle((BS / 2 - kw / 2, m, BS / 2 + kw / 2, BS * 0.40), fill=(46, 60, 140), outline=L, width=w)
    cd.ellipse((BS / 2 - BS * 0.12, BS * 0.40 - BS * 0.12, BS / 2 + BS * 0.12, BS * 0.40 + BS * 0.12), outline=L, width=w)
    cd.arc((BS * 0.06, -BS * 0.62, BS * 0.94, BS * 0.70), 0, 180, fill=L, width=w)
    cd.line((BS * 0.06, m, BS * 0.06, BS * 0.04), fill=L, width=w); cd.line((BS * 0.94, m, BS * 0.94, BS * 0.04), fill=L, width=w)
    cd.ellipse((BS / 2 - 26, BS * 0.11 - 26, BS / 2 + 26, BS * 0.11 + 26), outline=(255, 107, 53), width=7)
    cd.line((BS / 2 - 60, BS * 0.07, BS / 2 + 60, BS * 0.07), fill=L, width=w)
    cd.arc((BS / 2 - BS * 0.12, BS - m - BS * 0.12, BS / 2 + BS * 0.12, BS - m + BS * 0.12), 180, 360, fill=L, width=w)
    # frame + soft gold glow around the board
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((BX - 14, BY - 14, BX + BS + 14, BY + BS + 14), radius=40, fill=(255, 200, 60, 70))
    img = img.convert('RGBA'); img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(30)))
    mask = Image.new('L', (BS, BS), 0); ImageDraw.Draw(mask).rounded_rectangle((0, 0, BS, BS), radius=30, fill=255)
    img.paste(court, (BX, BY), mask)
    ImageDraw.Draw(img).rounded_rectangle((BX, BY, BX + BS, BY + BS), radius=30, outline=(74, 42, 18), width=8)
    # the 25 cells, faint
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    for i in range(25): ld.rounded_rectangle(cell_box(i), radius=12, fill=(255, 255, 255, 18), outline=(255, 255, 255, 120), width=3)
    img.alpha_composite(lay)
    return img

def target(img, i, lit=0.0):
    """one Fortress target: dimmed colour at rest, full colour + glow when lit (0..1)"""
    col = COL[i][0]; grow = int(12 * lit)
    if lit > 0:
        gl = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(gl).rounded_rectangle(cell_box(i, 26), radius=24, fill=col + (int(220 * lit),))
        img.alpha_composite(gl.filter(ImageFilter.GaussianBlur(28)))
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    a = int(110 + 145 * lit)
    ld.rounded_rectangle(cell_box(i, grow), radius=14, fill=col + (a,), outline=(255, 255, 255, int(255 * lit)) if lit else col + (180,), width=5)
    img.alpha_composite(lay)

def title(img, a, line1, l2a, l2b, col2=(255, 215, 0)):
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    f = G.anton(118); y0 = 205 - 40 * (1 - a)
    G.text_c(d, (540, y0), line1, f, G.WHITE)
    w1 = d.textlength(l2a, font=f); w2 = d.textlength(l2b, font=f); x = 540 - (w1 + w2) / 2
    d.text((x, y0 + 128), l2a, font=f, fill=G.WHITE, anchor='lm'); d.text((x + w1, y0 + 128), l2b, font=f, fill=col2, anchor='lm')
    if a < 1: lay.putalpha(lay.getchannel('A').point(lambda v: int(v * a)))
    img.alpha_composite(lay)

def faded(img, draw_fn, a):
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); draw_fn(ImageDraw.Draw(lay), lay)
    if a < 1: lay.putalpha(lay.getchannel('A').point(lambda v: int(v * a)))
    img.alpha_composite(lay)

def brand(img, tt, t0, line3):
    u = G.ease((tt - t0) / 0.4); a = int(255 * u)
    lay = Image.new('RGBA', (W, H), (8, 8, 20, int(215 * u))); ld = ImageDraw.Draw(lay)
    G.text_c(ld, (540, 860), 'COGNITIVO GYM', G.anton(130), G.ORANGE + (a,))
    G.text_c(ld, (540, 990), 'Entrena tu mente como entrenas tu juego', G.outfit(46, 600), (230, 230, 245, a))
    G.text_c(ld, (540, 1110), line3, G.outfit(46, 700), G.GOLD + (a,))
    img.alpha_composite(lay)

def lit_at(tt, t_start, step, on):
    """which chain step is lit at time tt, and how much (0..1)"""
    k = int((tt - t_start) // step)
    if tt < t_start or k >= len(CHAIN): return None, 0
    u = (tt - t_start - k * step) / on
    if u > 1: return None, 0
    return k, min(1, u / 0.15) * (1 - max(0, (u - 0.8) / 0.2))

# ─────────────────────────── the challenge ───────────────────────────
R_FLASH, R_STEP, R_ON = 2.3, 0.72, 0.55
R_END = R_FLASH + R_STEP * len(CHAIN)
R_ASK = R_END + 0.35
R_BRAND = R_ASK + 4.8
R_DUR = R_BRAND + 2.4

def frame_reto(tt):
    img = BG.copy()
    title(img, G.ease(tt / 0.3), '¿PUEDES RECORDAR', 'EL ', 'ORDEN?')
    if tt < R_BRAND: G.pill(img, 540, 82, 'TEST DE MEMORIA', G.outfit(34, 800), (255, 215, 0), (40, 30, 0))
    k, v = lit_at(tt, R_FLASH, R_STEP, R_ON)
    for i in COL: target(img, i, v if (k is not None and CHAIN[k] == i) else 0)
    if tt < R_FLASH:
        n = 3 - int((tt - 0.6) / 0.55) if tt >= 0.6 else None
        G.bottom(img, 'Memoriza el orden...', G.ease((tt - 0.2) / 0.3))
        if n is not None and 1 <= n <= 3:
            u = ((tt - 0.6) % 0.55) / 0.55
            faded(img, lambda d, l: G.text_c(d, (540, 1525), str(n), G.anton(int(110 * (1.25 - 0.25 * u))), G.GOLD), 1 - u * 0.6)
    elif tt < R_END:
        kk = min(len(CHAIN), int((tt - R_FLASH) // R_STEP) + 1)
        G.bottom(img, '¡Mira bien!', 1.0, G.GOLD)
        faded(img, lambda d, l: [d.ellipse((540 - 3 * 44 + j * 44 - 12 - 66 + 66, 1520 - 12, 540 - 3 * 44 + j * 44 + 12 - 66 + 66, 1520 + 12),
                                           fill=(255, 255, 255, 230) if j < kk else (255, 255, 255, 60)) for j in range(len(CHAIN))], 1.0)
    if R_ASK <= tt < R_BRAND:
        u = G.ease((tt - R_ASK) / 0.35)
        def q(d, l):
            for i, (c, name) in COL.items():
                x, y = cell_center(i)
                ly = y - 97 if i in (20, 24) else y + 97          # bottom row: name above, so it stays on the court
                d.rounded_rectangle((x - 92, ly - 22, x + 92, ly + 22), radius=22, fill=(10, 8, 26, 220))
                G.text_c(d, (x, ly), name, G.outfit(30, 800), c)
            d.rounded_rectangle((60, 1470, 1020, 1890), radius=44, fill=(10, 8, 26, 236), outline=(255, 215, 0, 255), width=4)
            G.text_c(d, (540, 1570), '¿QUÉ COLOR SE', G.anton(92), G.WHITE)
            G.text_c(d, (540, 1680), 'ENCENDIÓ DE 4TO?', G.anton(92), G.GOLD)
            G.text_c(d, (540, 1800), 'Comenta el color', G.outfit(54), (230, 230, 245))
        faded(img, q, u)
        left = max(0, 1 - (tt - R_ASK - 0.4) / (R_BRAND - R_ASK - 0.6))
        ImageDraw.Draw(img).rounded_rectangle((100, 1448, 100 + 880 * left, 1458), radius=5, fill=G.ORANGE)
    if tt >= R_BRAND: brand(img, tt, R_BRAND, '¿Lo recordaste? Comenta tu respuesta')
    return img.convert('RGB')

# ─────────────────────────── the answer ───────────────────────────
A_FLASH, A_STEP, A_ON = 1.6, 1.05, 0.8
A_END = A_FLASH + A_STEP * len(CHAIN)
A_ROLL = A_END + 0.3
A_REVEAL = A_ROLL + 1.3
A_BRAND = A_REVEAL + 3.4
A_DUR = A_BRAND + 2.4

def badges(d, upto, hi=None):
    """numbers left on the targets as the chain plays back"""
    seen = {}
    for j in range(upto):
        i = CHAIN[j]; n = seen.get(i, 0); seen[i] = n + 1
        x, y = cell_center(i); bx, by = x + 46, y - 46 + n * 62     # a second visit stacks below the first
        big = (j == hi)
        r = 34 if big else 28
        d.ellipse((bx - r, by - r, bx + r, by + r), fill=(255, 255, 255, 250) if not big else (255, 70, 70, 255), outline=(20, 16, 40, 255), width=3)
        G.text_c(d, (bx, by + 2), str(j + 1), G.anton(42 if big else 36), (20, 16, 40) if not big else G.WHITE)

def frame_resp(tt):
    img = BG.copy()
    title(img, G.ease(tt / 0.3), '¿LO RECORDASTE?', '', 'MÍRALO OTRA VEZ', (225, 220, 255))
    if tt < A_BRAND: G.pill(img, 540, 82, 'LA RESPUESTA', G.outfit(34, 800), (255, 70, 70), G.WHITE)
    k, v = lit_at(tt, A_FLASH, A_STEP, A_ON)
    hi_target = CHAIN[ASK] if tt >= A_REVEAL else None
    for i in COL:
        lit = v if (k is not None and CHAIN[k] == i) else 0
        if hi_target == i: lit = 0.75 + 0.25 * math.sin((tt - A_REVEAL) * 7)
        target(img, i, lit)
    done = 0 if tt < A_FLASH else min(len(CHAIN), int((tt - A_FLASH) // A_STEP) + 1)
    faded(img, lambda d, l: badges(d, done, ASK if tt >= A_REVEAL else None), 1.0)
    if tt < A_FLASH: G.bottom(img, 'Paso a paso...', G.ease((tt - 0.2) / 0.3))
    elif tt < A_ROLL: G.bottom(img, 'En cámara lenta...', 1.0, G.GOLD)
    elif tt < A_REVEAL: G.bottom(img, 'El 4to fue...', G.ease((tt - A_ROLL) / 0.25), G.WHITE, 66)
    if A_REVEAL <= tt < A_BRAND:
        u = G.ease((tt - A_REVEAL) / 0.3); sc = G.pop((tt - A_REVEAL) / 0.4)
        c, name = COL[CHAIN[ASK]]
        def r(d, l):
            d.rounded_rectangle((60, 1480, 1020, 1890), radius=44, fill=(10, 8, 26, 236), outline=c + (255,), width=5)
            G.text_c(d, (540, 1590), '¡ERA EL ' + name + '!', G.anton(int(108 * sc)), c)
            # the whole order, as coloured dots with their numbers
            n = len(CHAIN); gap = 120; x0 = 540 - gap * (n - 1) / 2
            for j, i in enumerate(CHAIN):
                x = x0 + j * gap; cc = COL[i][0]; rr = 40 if j == ASK else 32
                d.rounded_rectangle((x - rr, 1720 - rr, x + rr, 1720 + rr), radius=12, fill=cc + (255,), outline=(255, 255, 255, 255 if j == ASK else 90), width=4)
                G.text_c(d, (x, 1722), str(j + 1), G.anton(40), (20, 16, 40))
            G.text_c(d, (540, 1835), '¿Acertaste? Cuéntanos', G.outfit(46), G.GOLD)
        faded(img, r, u)
    if tt >= A_BRAND: brand(img, tt, A_BRAND, 'Un reto nuevo cada semana')
    return img.convert('RGB')

BG = None
if __name__ == '__main__':
    which, mode = sys.argv[1], sys.argv[2]
    BG = background()
    if which == 'reto':
        fr, dur = frame_reto, R_DUR
        info = {'duration': round(R_DUR, 2), 't_show': 0.0, 't_hide': R_FLASH, 't_stop': round(R_END, 3), 't_ask': round(R_ASK, 3), 't_brand': round(R_BRAND, 3),
                'flashes': [[round(R_FLASH + j * R_STEP, 3), PITCH[i]] for j, i in enumerate(CHAIN)], 'roll': False}
        name = 'fortress-orden'
    else:
        fr, dur = frame_resp, A_DUR
        info = {'duration': round(A_DUR, 2), 't_show': 0.0, 't_hide': A_FLASH, 't_stop': round(A_END, 3), 't_ask': round(A_ROLL, 3), 't_reveal': round(A_REVEAL, 3),
                't_brand': round(A_BRAND, 3), 'flashes': [[round(A_FLASH + j * A_STEP, 3), PITCH[i]] for j, i in enumerate(CHAIN)]}
        name = 'fortress-orden-respuesta'
    json.dump(info, open('info-' + name + '.json', 'w'))
    print(name, info['duration'], 'answer', COL[CHAIN[ASK]][1])
    if mode == 'preview':
        pts = [0.9, R_FLASH + 0.2, R_FLASH + 3 * R_STEP + 0.2, R_ASK + 1.0, R_BRAND + 1.2] if which == 'reto' else [0.8, A_FLASH + 3 * A_STEP + 0.3, A_REVEAL + 1.0]
        for t in pts: fr(t).save('pv-%s-%05.2f.png' % (which, t))
    else:
        tmp = name + '-video.tmp.mp4'
        p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '%dx%d' % (W, H), '-r', str(FPS), '-i', '-',
                              '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', tmp], stdin=subprocess.PIPE)
        for f in range(int(dur * FPS)): p.stdin.write(fr(f / FPS).tobytes())
        p.stdin.close(); p.wait()
        if p.returncode == 0: os.replace(tmp, name + '-video.mp4')
        print('done', p.returncode)
