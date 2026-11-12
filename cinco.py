# "¿Quién tiene el balón? 5 balones" — the ball to follow starts with #7.
# On every pass one more identical ball flies in from the sideline, until
# all five players hold one. Then the big final shuffle: players swap balls
# in pairs, two swaps at a time, faster and faster. Lights out: who has it?
# Same court and players as quien.py.
#   python3 cinco.py reto preview|render       -> cinco-video.mp4 (silent)
#   python3 cinco.py respuesta preview|render  -> cinco-respuesta-video.mp4
import sys, os, math, json, random, subprocess
from PIL import Image, ImageDraw, ImageFilter
import sigue as G
import quien as Q

W, H, FPS = G.W, G.H, G.FPS
SPOTS, NUMS, OK = Q.SPOTS, Q.NUMS, Q.OK
NB = 5

def desde(i):
    """where a new ball flies in from: off the nearest sideline"""
    return (-120 if SPOTS[i][0] < 540 else W + 120, SPOTS[i][1] - 60)

# ── the plan ───────────────────────────────────────────────────────────
#   moves[b] = list of (t0, t1, from_xy, to_player); a ball appears at its
#   first move. Build-up: ball 0 (the one to follow) passes to a free
#   player while a new ball flies in to another free player. Shuffle:
#   pairs of players swap balls, two swaps at once, never on a lane that
#   crosses a third player.
ARMADO = [0.78, 0.72, 0.66, 0.60]                         # 4 build-up passes -> 5 balls
MEZCLA = [0.56, 0.52, 0.48, 0.45, 0.42, 0.40, 0.37, 0.35, 0.33, 0.31, 0.30, 0.29]
SEED = int(os.environ.get('CINCO_SEED', '4'))          # a team version uses its own, so its answer differs

def plan(seed):
    rnd = random.Random(seed)
    tiene = {0: 0}                                          # ball -> player
    moves = {b: [] for b in range(NB)}
    beats = []                                              # (t0, t1) of every beat, for the music
    t = 2.3
    for k, d in enumerate(ARMADO):
        libres = [j for j in range(5) if j not in tiene.values()]
        de = tiene[0]
        a = rnd.choice([j for j in libres if (de, j) in OK])
        moves[0].append((t, t + d, de, a)); tiene[0] = a
        libres = [j for j in range(5) if j not in tiene.values()]
        nuevo = rnd.choice(libres); b = k + 1
        moves[b].append((t, t + d, 'in', nuevo)); tiene[b] = nuevo
        beats.append((t, t + d)); t += d + 0.16
    t += 0.35                                               # a breath: all five hold a ball
    t_mezcla = t
    jugador = {p: b for b, p in tiene.items()}              # player -> ball
    sigue_veces = 0
    for k, d in enumerate(MEZCLA):
        for _ in range(500):
            p = rnd.sample(range(5), 4); s1, s2 = (p[0], p[1]), (p[2], p[3])
            if s1 in OK and s2 in OK: break
        for (x, y) in (s1, s2):
            bx, by = jugador[x], jugador[y]
            moves[bx].append((t, t + d, x, y)); moves[by].append((t, t + d, y, x))
            jugador[x], jugador[y] = by, bx
            if 0 in (bx, by): sigue_veces += 1
        beats.append((t, t + d)); t += d + max(0.05, 0.12 - 0.006 * k)
    final = {b: p for p, b in jugador.items()}
    return moves, beats, final, t_mezcla, t - 0.05, sigue_veces

MOVES, BEATS, FINAL_DE, T_MEZCLA, T_STOP, VECES = plan(SEED)
FINAL = FINAL_DE[0]

def lugar(b, g):
    """(x, y, scale, visible) of ball b at game time g"""
    mv = MOVES[b]
    if not mv or g < mv[0][0] and b != 0: return 0, 0, 1, False
    h = mv[0][2] if b == 0 else None
    for (a, z, de, para) in mv:
        if g < a: break
        if g < z:
            p = desde(para) if de == 'in' else Q.mano(de)
            x, y, sc = Q.vuelo(p, Q.mano(para), (g - a) / (z - a)); return x, y, sc, True
        h = para
    x, y = Q.mano(h); return x, y, 1.0, True

def jugadores(img, tt0=None, tt=0, hot=None, dim=False):
    for k, (x, y) in enumerate(SPOTS):
        a = 1 if tt0 is None else G.ease((tt - tt0 - 0.07 * k) / 0.3)
        if a <= 0: continue
        spr = Q.TOK_HOT[k] if k == hot else Q.TOK_DIM[k] if dim else Q.TOK[k]
        G.paste_c(img, spr, x, y, a, 0.6 + 0.4 * a)

def cuenta(img, n, a=1.0):
    """how many balls are in play, top of the court"""
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    s = '%d %s' % (n, 'BALÓN' if n == 1 else 'BALONES')
    tw = d.textlength(s, font=G.bebas(64))
    d.rounded_rectangle((540 - tw / 2 - 34, 860, 540 + tw / 2 + 34, 948), radius=44, fill=G.CG_DARK + (int(220 * a),))
    G.text_c(d, (540, 906), s, G.bebas(64), G.CG_GOLD + (int(255 * a),))
    img.alpha_composite(lay)

def en_juego(g):
    return sum(1 for b in range(NB) if lugar(b, g)[3])

# ── the challenge ──
T_SHOW, T_HIDE = 0.4, 2.1
T_ASK = T_STOP + 0.55
T_BRAND = T_ASK + 4.2
DUR = T_BRAND + 2.4

def frame_reto(tt):
    img = G.BG.copy().convert('RGBA')
    flick = any(abs(tt - (BEATS[k][0] + 0.1)) < 0.05 for k in (-3, -2))
    if flick: Q.apagon(img, 0.55)
    if tt >= T_STOP: Q.apagon(img, G.ease((tt - T_STOP) / 0.08))
    if tt < T_BRAND: G.wordmark(img)
    G.title(img, G.ease(tt / 0.3), '¿QUIÉN TIENE', 'EL ', 'BALÓN?')
    jugadores(img, 0.1, tt, dim=T_STOP <= tt < T_ASK)     # dark only for the lights-out moment; bright again for the question
    if tt < T_STOP:
        for b in range(1, NB):
            x, y, sc, v = lugar(b, tt)
            if v: Q.pelota(img, x, y, sc)
        x, y, sc, _ = lugar(0, tt)
        if tt > 0.3: Q.pelota(img, x, y, sc * G.ease((tt - 0.3) / 0.25), hot=T_SHOW <= tt < T_HIDE)
        if tt < T_MEZCLA: cuenta(img, en_juego(tt), G.ease((tt - 0.6) / 0.3))
    if T_SHOW <= tt < T_HIDE:
        x, y = Q.mano(0); ph = tt - T_SHOW; rr = 62 * Q.BR + 16 + 7 * math.sin(ph * 7)
        ImageDraw.Draw(img).ellipse((x - rr, y - rr, x + rr, y + rr), outline=G.RED, width=7)
        a = G.ease(ph / 0.3) * (1 - G.ease((tt - (T_HIDE - 0.3)) / 0.3))
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        ld.rounded_rectangle((x + 80, y - 44, x + 380, y + 44), radius=44, fill=(255, 70, 70, 235))
        ld.polygon([(x + 64, y), (x + 88, y - 18), (x + 88, y + 18)], fill=(255, 70, 70, 235))
        G.text_c(ld, (x + 230, y + 2), 'SIGUE ESTE', G.outfit(42, 800), G.WHITE)
        lay.putalpha(lay.getchannel('A').point(lambda v: int(v * a))); img.alpha_composite(lay)
        G.bottom(img, 'Cada pase, entra otro balón', G.ease(ph / 0.3), size=56)
    elif T_HIDE <= tt < T_MEZCLA - 0.2:
        G.bottom(img, '¡No lo pierdas!', 1.0, G.CG_GOLD)
    elif tt < T_MEZCLA + 1.2:
        G.bottom(img, '¡A MEZCLAR!', G.ease((tt - T_MEZCLA + 0.2) / 0.2), G.CG_ORANGE, 70)
    elif tt < T_STOP:
        G.bottom(img, '¡Más rápido!', 1.0, G.CG_ORANGE)
    elif tt < T_ASK:
        G.bottom(img, '¡Se fue la luz!', G.ease((tt - T_STOP) / 0.15), G.CG_GOLD, 66)
    if T_ASK <= tt < T_BRAND:
        u = G.ease((tt - T_ASK) / 0.35)
        Q.caja(img, u, '¿QUIÉN TIENE EL BALÓN?', 'Empezó con el ' + NUMS[0] + ' · Comenta el número', G.CG_GOLD)
        left = max(0, 1 - (tt - T_ASK - 0.4) / (T_BRAND - T_ASK - 0.6))
        ImageDraw.Draw(img).rounded_rectangle((120, 1682, 120 + 840 * left, 1692), radius=5, fill=G.CG_ORANGE)
    if tt >= T_BRAND:
        G.endcard_brillante(img, G.ease((tt - T_BRAND) / 0.4), '¿Lo viste? Comenta el número')
    return img.convert('RGB')

# ── the answer: slow motion, every ball shown as it comes in; the ball to
#    follow stays red with a trail, drawn on top the whole way ──
SLOW = 0.7
T0 = 1.4
G0 = MOVES[0][0][0]
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
    jugadores(img, hot=FINAL if tt >= T_REVEAL_R else None)
    if tt < T_REVEAL_R:
        for b in range(1, NB):
            x, y, sc, v = lugar(b, g)
            if v: Q.pelota(img, x, y, sc)                      # the others at full strength, as they come in
        if tt >= T0:
            for i in range(12, 0, -1):
                x, y, _, _ = lugar(0, max(G0, g - i * 0.03)); r = 22 - i * 1.4
                tl = Image.new('RGBA', (W, H), (0, 0, 0, 0))
                ImageDraw.Draw(tl).ellipse((x - r, y - r, x + r, y + r), fill=(255, 70, 70, int(140 * (1 - i / 13))))
                img.alpha_composite(tl)
        x, y, sc, _ = lugar(0, g); Q.pelota(img, x, y, sc, hot=True)
        rr = (62 * Q.BR + 14) * sc + 5 * math.sin(tt * 7)              # a red ring that never leaves it
        ring = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(ring).ellipse((x - rr, y - rr, x + rr, y + rr), outline=(255, 70, 70, 255), width=8)
        img.alpha_composite(ring.filter(ImageFilter.GaussianBlur(5))); img.alpha_composite(ring)
    if tt < T0:
        G.bottom(img, 'Empieza con el ' + NUMS[0], G.ease((tt - 0.2) / 0.3))
    elif tt < T_STOP_R + 0.05:
        G.bottom(img, 'Sigue el rojo', 1.0, G.CG_GOLD)
    elif tt < T_REVEAL_R:
        G.bottom(img, 'Lo tiene...', G.ease((tt - T_ROLL_R) / 0.25), G.WHITE, 66)
    if T_REVEAL_R <= tt < T_BRAND_R:
        sc = G.pop((tt - T_REVEAL_R) / 0.4); u = G.ease((tt - T_REVEAL_R) / 0.3)
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        ld.rounded_rectangle((90, 1700, 990, 1890), radius=26, fill=G.CG_DARK + (238,), outline=(255, 70, 70, 255), width=4)
        G.text_c(ld, (540, 1762), '¡ERA EL ' + NUMS[FINAL] + '!', G.bebas(int(118 * sc)), G.WHITE)
        G.text_c(ld, (540, 1850), '¿Acertaste? Cuéntanos', G.outfit(48), G.CG_GOLD)
        lay.putalpha(lay.getchannel('A').point(lambda v: int(v * u))); img.alpha_composite(lay)
    if tt >= T_BRAND_R:
        G.endcard_brillante(img, G.ease((tt - T_BRAND_R) / 0.4), 'Un reto nuevo cada semana')
    return img.convert('RGB')

if __name__ == '__main__':
    modo = sys.argv[1]; acc = sys.argv[2] if len(sys.argv) > 2 else 'preview'
    G.BG = G.background(); Q.MODO = modo
    if modo == 'reto':
        info = {'duration': round(DUR, 2), 't_show': T_SHOW, 't_hide': T_HIDE, 't_stop': round(T_STOP, 3), 't_ask': round(T_ASK, 3),
                't_brand': round(T_BRAND, 3), 'swap_times': [(round(a, 3), round(b, 3)) for a, b in BEATS], 'answer': NUMS[FINAL]}
        json.dump(info, open('info-cinco.json', 'w')); print(info['duration'], 'answer', NUMS[FINAL], 'times the followed ball moved in the shuffle:', VECES)
        if acc == 'preview':
            for tt in [1.2, BEATS[1][0] + 0.3, BEATS[3][1] + 0.2, T_MEZCLA + 2.0, T_STOP + 0.3]: frame_reto(tt).save('k-%05.2f.png' % tt)
        else: Q.render(frame_reto, DUR, 'cinco-video.mp4')
    else:
        info = {'duration': round(DUR_R, 2), 't_show': 0.0, 't_hide': T0, 't_stop': round(T_STOP_R, 3), 't_ask': round(T_ROLL_R, 3),
                't_reveal': round(T_REVEAL_R, 3), 't_brand': round(T_BRAND_R, 3),
                'swap_times': [(round(T0 + (a - G0) / SLOW, 3), round(T0 + (b - G0) / SLOW, 3)) for a, b in BEATS]}
        json.dump(info, open('info-cinco-respuesta.json', 'w')); print(info['duration'], 'answer', NUMS[FINAL])
        if acc == 'preview':
            for tt in [0.8, T0 + 3.0, T_REVEAL_R + 0.8]: frame_resp(tt).save('kr-%05.2f.png' % tt)
        else: Q.render(frame_resp, DUR_R, 'cinco-respuesta-video.mp4')
