# Challenges 3 and 4, on the same court as the Fortress one.
#   3 · The Recall — "¿Puedes recordar los números?": five numbers appear on the
#       court one at a time, then vanish; four squares get a letter.
#   4 · The Recognition — "¿Cuál cambió?": a gold pattern, then its
#       echo in lime with ONE square moved; every square gets a letter.
# Each has an answer video.
#   python3 recall_recog.py recall|recall-resp|recog|recog-resp preview|render
import sys, os, math, json, subprocess
from PIL import Image, ImageDraw
import sigue as G
import fortress as F

W, H, FPS = 1080, 1920, 30
ORANGE = (255, 107, 53); LIME = (154, 205, 50); GOLDC = (255, 215, 0)
LET = 'ABCDEF'

# ── challenge 3: The Recall ──
NUMS = {1: 6, 2: 13, 3: 19, 4: 2, 5: 22}          # number -> cell
CAND = [2, 13, 19, 22]                            # lettered A..D in reading order
ASK_NUM = 3
RC_ANS = LET[CAND.index(NUMS[ASK_NUM])]           # 'C'
RC_PITCH = {1: 392, 2: 440, 3: 494, 4: 523, 5: 587}

# ── challenge 4: The Recognition ──
ORIG = [1, 7, 11, 13, 17, 23]
ECHO = [1, 7, 11, 13, 18, 23]                     # 17 moved to 18
MOVED_FROM, MOVED_TO = 17, 18
RG_ANS = LET[ECHO.index(MOVED_TO)]                # 'E'

def num_cell(img, i, n, col=ORANGE, a=1.0, ring=None):
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle(F.cell_box(i, 4), radius=14, fill=col + (240,), outline=(255, 255, 255, 230), width=4)
    G.text_c(d, F.cell_center(i), str(n), G.anton(84), G.WHITE)
    if ring: x, y = F.cell_center(i); r = 92; d.ellipse((x - r, y - r, x + r, y + r), outline=ring + (255,), width=8)
    if a < 1: lay.putalpha(lay.getchannel('A').point(lambda v: int(v * a)))
    img.alpha_composite(lay)

def fill_cell(img, i, col, a=1.0, outline=None, dashed=False):
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    if dashed:
        x0, y0, x1, y1 = F.cell_box(i, 2)
        for t in range(0, 100, 14):
            for (ax, ay, bx, by) in [(x0, y0, x1, y0), (x1, y0, x1, y1), (x1, y1, x0, y1), (x0, y1, x0, y0)]:
                u0, u1 = t / 100, min(1, (t + 7) / 100)
                d.line((ax + (bx - ax) * u0, ay + (by - ay) * u0, ax + (bx - ax) * u1, ay + (by - ay) * u1), fill=col + (255,), width=6)
    else:
        d.rounded_rectangle(F.cell_box(i, 4), radius=14, fill=col + (235,), outline=outline + (255,) if outline else (255, 255, 255, 120), width=4)
    if a < 1: lay.putalpha(lay.getchannel('A').point(lambda v: int(v * a)))
    img.alpha_composite(lay)

def letter(img, i, ch, a=1.0, hot=False, scale=1.0):
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    x, y = F.cell_center(i); r = 40 * scale
    d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 70, 70, 255) if hot else (255, 255, 255, 245), outline=(20, 16, 40, 255), width=4)
    G.text_c(d, (x, y + 3), ch, G.anton(int(54 * scale)), G.WHITE if hot else (20, 16, 40))
    if a < 1: lay.putalpha(lay.getchannel('A').point(lambda v: int(v * a)))
    img.alpha_composite(lay)

def countdown(img, tt, t0, words):
    G.bottom(img, words, G.ease((tt - 0.2) / 0.3))
    if tt >= t0:
        n = 3 - int((tt - t0) / 0.5)
        if 1 <= n <= 3:
            u = ((tt - t0) % 0.5) / 0.5
            F.faded(img, lambda d, l: G.text_c(d, (540, 1525), str(n), G.anton(int(110 * (1.25 - 0.25 * u))), G.GOLD), 1 - u * 0.6)

def ask_box(img, tt, t0, t_end, l1, l2, l3, col):
    u = G.ease((tt - t0) / 0.35)
    def q(d, l):
        d.rounded_rectangle((60, 1470, 1020, 1890), radius=44, fill=(10, 8, 26, 236), outline=col + (255,), width=4)
        G.text_c(d, (540, 1570), l1, G.anton(92), G.WHITE)
        G.text_c(d, (540, 1680), l2, G.anton(92), col)
        G.text_c(d, (540, 1800), l3, G.outfit(54), (230, 230, 245))
    F.faded(img, q, u)
    left = max(0, 1 - (tt - t0 - 0.4) / (t_end - t0 - 0.6))
    ImageDraw.Draw(img).rounded_rectangle((100, 1448, 100 + 880 * left, 1458), radius=5, fill=G.ORANGE)

def reveal_box(img, tt, t0, big, col, line):
    u = G.ease((tt - t0) / 0.3); sc = G.pop((tt - t0) / 0.4)
    def r(d, l):
        d.rounded_rectangle((60, 1480, 1020, 1890), radius=44, fill=(10, 8, 26, 236), outline=col + (255,), width=5)
        G.text_c(d, (540, 1620), big, G.anton(int(116 * sc)), col)
        G.text_c(d, (540, 1780), line, G.outfit(48), G.GOLD)
    F.faded(img, r, u)

# ─────────── 3 · The Recall: challenge ───────────
C_IN, C_STEP = 2.0, 0.75
C_ALL = C_IN + C_STEP * 5                 # all five on the court
C_GONE = C_ALL + 1.0                      # they vanish
C_ASK = C_GONE + 0.6
C_BRAND = C_ASK + 4.8
C_DUR = C_BRAND + 2.4

def f_recall(tt):
    img = BG.copy()
    F.title(img, G.ease(tt / 0.3), '¿PUEDES RECORDAR', 'LOS ', 'NÚMEROS?', ORANGE)   # the question comes only at the end
    if tt < C_BRAND: G.pill(img, 540, 82, 'TEST DE MEMORIA', G.outfit(34, 800), ORANGE, G.WHITE)
    shown = 0 if tt < C_IN else min(5, int((tt - C_IN) / C_STEP) + 1)
    a = 1 - G.ease((tt - C_GONE + 0.3) / 0.3)
    for n in range(1, shown + 1):
        sc_a = G.ease((tt - C_IN - (n - 1) * C_STEP) / 0.15)
        if a > 0: num_cell(img, NUMS[n], n, a=min(a, sc_a))
    if tt < C_IN: countdown(img, tt, 0.5, 'Memoriza dónde sale cada uno...')
    elif tt < C_GONE: G.bottom(img, '¡Fíjate bien!', 1.0, G.GOLD)
    if C_ASK <= tt < C_BRAND:
        u = G.ease((tt - C_ASK) / 0.3)
        for k, i in enumerate(CAND): letter(img, i, LET[k], u)
        ask_box(img, tt, C_ASK, C_BRAND, '¿DÓNDE ESTABA', 'EL NÚMERO 3?', 'Comenta A, B, C o D', ORANGE)
    if tt >= C_BRAND: F.brand(img, tt, C_BRAND, '¿Lo recordaste? Comenta tu letra')
    return img.convert('RGB')

# ─────────── 3 · The Recall: answer ───────────
CA_IN, CA_STEP = 1.4, 1.0
CA_ALL = CA_IN + CA_STEP * 5
CA_ROLL = CA_ALL + 0.4
CA_REV = CA_ROLL + 1.3
CA_BRAND = CA_REV + 3.4
CA_DUR = CA_BRAND + 2.4

def f_recall_resp(tt):
    img = BG.copy()
    F.title(img, G.ease(tt / 0.3), '¿LO RECORDASTE?', '', 'MÍRALO OTRA VEZ', (225, 220, 255))
    if tt < CA_BRAND: G.pill(img, 540, 82, 'LA RESPUESTA', G.outfit(34, 800), (255, 70, 70), G.WHITE)
    shown = 0 if tt < CA_IN else min(5, int((tt - CA_IN) / CA_STEP) + 1)
    for n in range(1, shown + 1):
        hot = (n == ASK_NUM and tt >= CA_REV)
        num_cell(img, NUMS[n], n, ORANGE if not hot else (255, 70, 70), 1.0 if (tt < CA_REV or hot) else 0.45,
                 ring=(255, 255, 255) if hot else None)
    if tt >= CA_ROLL:
        u = G.ease((tt - CA_ROLL) / 0.3)
        for k, i in enumerate(CAND):
            x, y = F.cell_center(i)
            lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
            hot = (LET[k] == RC_ANS and tt >= CA_REV); r = 30 if not hot else 36
            cx, cy = x + 52, y - 52
            d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 70, 70, 255) if hot else (255, 255, 255, 245), outline=(20, 16, 40, 255), width=3)
            G.text_c(d, (cx, cy + 2), LET[k], G.anton(40 if not hot else 48), G.WHITE if hot else (20, 16, 40))
            lay.putalpha(lay.getchannel('A').point(lambda v: int(v * u))); img.alpha_composite(lay)
    if tt < CA_IN: G.bottom(img, 'Paso a paso...', G.ease((tt - 0.2) / 0.3))
    elif tt < CA_ROLL: G.bottom(img, 'Así salieron los números', 1.0, G.GOLD)
    elif tt < CA_REV: G.bottom(img, 'El 3 estaba en...', G.ease((tt - CA_ROLL) / 0.25), G.WHITE, 66)
    if CA_REV <= tt < CA_BRAND: reveal_box(img, tt, CA_REV, '¡ERA LA ' + RC_ANS + '!', ORANGE, '¿Acertaste? Cuéntanos')
    if tt >= CA_BRAND: F.brand(img, tt, CA_BRAND, 'Un reto nuevo cada semana')
    return img.convert('RGB')

# ─────────── 4 · The Recognition: challenge ───────────
G_ORIG, G_ORIG_END = 2.0, 4.6
G_ECHO, G_ECHO_END = 5.2, 7.6
G_ASK = G_ECHO_END
G_BRAND = G_ASK + 5.0
G_DUR = G_BRAND + 2.4

def f_recog(tt):
    img = BG.copy()
    F.title(img, G.ease(tt / 0.3), '¿VES EL', '', 'CAMBIO?', LIME)
    if tt < G_BRAND: G.pill(img, 540, 82, 'TEST DE ATENCIÓN', G.outfit(34, 800), LIME, (20, 30, 0))
    if G_ORIG <= tt < G_ORIG_END:
        a = G.ease((tt - G_ORIG) / 0.2) * (1 - G.ease((tt - G_ORIG_END + 0.25) / 0.25))
        for i in ORIG: fill_cell(img, i, GOLDC, a)
    if tt >= G_ECHO:
        a = G.ease((tt - G_ECHO) / 0.2)
        for i in ECHO: fill_cell(img, i, LIME, a)
    if tt < G_ORIG: countdown(img, tt, 0.5, 'Memoriza el patrón...')
    elif tt < G_ECHO: G.bottom(img, 'ORIGINAL — memorízalo', 1.0, G.GOLD)
    elif tt < G_ASK: G.bottom(img, 'Ahora el eco: UNA cambió', 1.0, LIME)
    if G_ASK <= tt < G_BRAND:
        u = G.ease((tt - G_ASK) / 0.3)
        for k, i in enumerate(ECHO): letter(img, i, LET[k], u)
        ask_box(img, tt, G_ASK, G_BRAND, '¿CUÁL CAMBIÓ', 'DE LUGAR?', 'Comenta la letra', LIME)
    if tt >= G_BRAND: F.brand(img, tt, G_BRAND, '¿La viste? Comenta tu letra')
    return img.convert('RGB')

# ─────────── 4 · The Recognition: answer ───────────
GA_ORIG, GA_ECHO = 1.4, 4.2
GA_ROLL = 6.6
GA_REV = GA_ROLL + 1.3
GA_BRAND = GA_REV + 3.6
GA_DUR = GA_BRAND + 2.4

def f_recog_resp(tt):
    img = BG.copy()
    F.title(img, G.ease(tt / 0.3), '¿LA VISTE?', '', 'MÍRALO OTRA VEZ', (225, 220, 255))
    if tt < GA_BRAND: G.pill(img, 540, 82, 'LA RESPUESTA', G.outfit(34, 800), (255, 70, 70), G.WHITE)
    if GA_ORIG <= tt < GA_ECHO:
        for i in ORIG: fill_cell(img, i, GOLDC, G.ease((tt - GA_ORIG) / 0.2))
    if tt >= GA_ECHO:
        for i in ORIG:
            if i not in ECHO: fill_cell(img, i, GOLDC, 1.0, dashed=True)       # where it was
        for i in ECHO:
            moved = (i == MOVED_TO and tt >= GA_REV)
            fill_cell(img, i, (255, 70, 70) if moved else LIME, 1.0 if (tt < GA_REV or moved) else 0.5, outline=(255, 255, 255) if moved else None)
        if tt >= GA_ROLL:
            u = G.ease((tt - GA_ROLL) / 0.3)
            for k, i in enumerate(ECHO):
                hot = (LET[k] == RG_ANS and tt >= GA_REV)
                letter(img, i, LET[k], u, hot, G.pop((tt - GA_REV) / 0.4) if hot else 1.0)
    if tt < GA_ORIG: G.bottom(img, 'El original...', G.ease((tt - 0.2) / 0.3))
    elif tt < GA_ECHO: G.bottom(img, 'ORIGINAL', 1.0, G.GOLD)
    elif tt < GA_ROLL: G.bottom(img, 'El eco, con el original punteado', 1.0, LIME, 56)
    elif tt < GA_REV: G.bottom(img, 'La que cambió fue...', G.ease((tt - GA_ROLL) / 0.25), G.WHITE, 66)
    if GA_REV <= tt < GA_BRAND: reveal_box(img, tt, GA_REV, '¡ERA LA ' + RG_ANS + '!', LIME, 'Se movió un cuadro a la derecha')
    if tt >= GA_BRAND: F.brand(img, tt, GA_BRAND, 'Un reto nuevo cada semana')
    return img.convert('RGB')

BG = None
if __name__ == '__main__':
    which, mode = sys.argv[1], sys.argv[2]
    BG = F.background()
    if which == 'recall':
        fr, dur, name = f_recall, C_DUR, 'recall-donde-3'
        info = {'t_show': 0, 't_hide': C_IN, 't_stop': C_GONE, 't_ask': C_ASK, 't_brand': C_BRAND, 'roll': False,
                'flashes': [[C_IN + (n - 1) * C_STEP, RC_PITCH[n]] for n in range(1, 6)]}
        pts = [1.2, C_IN + 3.2, C_ASK + 1.0]
    elif which == 'recall-resp':
        fr, dur, name = f_recall_resp, CA_DUR, 'recall-donde-3-respuesta'
        info = {'t_show': 0, 't_hide': CA_IN, 't_stop': CA_ALL, 't_ask': CA_ROLL, 't_reveal': CA_REV, 't_brand': CA_BRAND,
                'flashes': [[CA_IN + (n - 1) * CA_STEP, RC_PITCH[n]] for n in range(1, 6)]}
        pts = [CA_IN + 4.3, CA_REV + 1.0]
    elif which == 'recog':
        fr, dur, name = f_recog, G_DUR, 'recognition-cambio'
        info = {'t_show': 0, 't_hide': G_ORIG, 't_stop': G_ECHO_END, 't_ask': G_ASK, 't_brand': G_BRAND, 'roll': False,
                'flashes': [[G_ORIG, 523], [G_ORIG + 0.05, 659], [G_ECHO, 587], [G_ECHO + 0.05, 740]]}
        pts = [G_ORIG + 1.0, G_ECHO + 1.0, G_ASK + 1.0]
    else:
        fr, dur, name = f_recog_resp, GA_DUR, 'recognition-cambio-respuesta'
        info = {'t_show': 0, 't_hide': GA_ORIG, 't_stop': GA_ECHO, 't_ask': GA_ROLL, 't_reveal': GA_REV, 't_brand': GA_BRAND,
                'flashes': [[GA_ORIG, 523], [GA_ORIG + 0.05, 659], [GA_ECHO, 587], [GA_ECHO + 0.05, 740]]}
        pts = [GA_ECHO + 1.0, GA_REV + 1.0]
    info['duration'] = round(dur, 2)
    info = {k: (round(v, 3) if isinstance(v, float) else v) for k, v in info.items()}
    json.dump(info, open('info-' + name + '.json', 'w'))
    print(name, info['duration'], 'answer', RC_ANS if which.startswith('recall') else RG_ANS)
    if mode == 'preview':
        for t in pts: fr(t).save('pv-%s-%05.2f.png' % (which, t))
    else:
        tmp = name + '-video.tmp.mp4'
        p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '%dx%d' % (W, H), '-r', str(FPS), '-i', '-',
                              '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', tmp], stdin=subprocess.PIPE)
        for f in range(int(dur * FPS)): p.stdin.write(fr(f / FPS).tobytes())
        p.stdin.close(); p.wait()
        if p.returncode == 0: os.replace(tmp, name + '-video.mp4')
        print('done', p.returncode)
