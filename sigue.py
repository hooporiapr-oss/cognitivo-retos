# "¿Puedes seguir el balón?" — attention challenge, 1080x1920 portrait.
# python3 sigue.py preview   -> a few still frames
# python3 sigue.py render    -> sigue-el-balon.mp4 (silent; music added after)
import sys, math, random, subprocess, os, json
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = HERE
W, H, FPS = 1080, 1920, 30
ANTON = os.path.join(HERE, 'Anton.woff')
OUTF = os.path.join(HERE, 'Outfit-{}.woff')
def anton(n): return ImageFont.truetype(ANTON, n)
def outfit(n, w=700): return ImageFont.truetype(OUTF.format(w), n)

ORANGE = (255, 122, 24); NEON = (150, 110, 255); CYAN = (90, 230, 255); WHITE = (255, 255, 255)
GREEN = (120, 230, 120); RED = (255, 70, 70); GOLD = (255, 205, 60)

# ── the three spots: above the head, left hand, right hand ──
SPOTS = [(540, 470), (318, 1205), (762, 1205)]
CENTROID = (540, 960)

# ── timeline ──
T_INTRO, T_SHOW, T_HIDE = 0.0, 0.45, 3.0     # the red ball is marked almost at once          # title in · "this one" · all look the same
random.seed(23)
swaps, t = [], 3.55
durs = [0.80, 0.76, 0.72, 0.66, 0.62, 0.58, 0.54, 0.50, 0.47, 0.44, 0.42, 0.40, 0.38, 0.36, 0.35, 0.34, 0.33, 0.32]
last = None
for d in durs:
    pairs = [p for p in [(0, 1), (0, 2), (1, 2)] if p != last]
    p = random.choice(pairs); last = p
    swaps.append((t, t + d, p)); t += d + 0.07
T_STOP = t + 0.25
T_ASK = T_STOP + 0.35
T_END = T_ASK + 4.6                                  # question + countdown
T_BRAND = T_END
DUR = T_BRAND + 2.4

# where each ball sits after every swap; ball 0 is the one to follow
def positions_at(tt):
    """returns list of (x,y) for balls 0,1,2 and a 'moving' flag"""
    slot = [0, 1, 2]                                 # slot[ball] = spot index
    for (a, b, (i, j)) in swaps:
        if tt < a: break
        bi = slot.index(i); bj = slot.index(j)
        if tt < b:
            u = (tt - a) / (b - a); u = u * u * (3 - 2 * u)
            pos = [SPOTS[s] for s in slot]
            pos[bi] = arc(SPOTS[i], SPOTS[j], u, +1)
            pos[bj] = arc(SPOTS[j], SPOTS[i], u, +1)
            return pos, True
        slot[bi], slot[bj] = j, i
    return [SPOTS[s] for s in slot], False

def final_spot():
    slot = [0, 1, 2]
    for (_, _, (i, j)) in swaps:
        bi = slot.index(i); bj = slot.index(j); slot[bi], slot[bj] = j, i
    return slot[0]

def arc(p, q, u, side):
    """curved path from p to q bulging to one side, so two balls swapping never overlap"""
    mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
    dx, dy = q[0] - p[0], q[1] - p[1]
    L = math.hypot(dx, dy) or 1
    nx, ny = -dy / L, dx / L
    k = 0.32 * L * side
    cx, cy = mx + nx * k, my + ny * k
    x = (1 - u) ** 2 * p[0] + 2 * (1 - u) * u * cx + u * u * q[0]
    y = (1 - u) ** 2 * p[1] + 2 * (1 - u) * u * cy + u * u * q[1]
    return (x, y)

# ── static background: night gradient, faint stars, the neon player ──
def background():
    g = np.zeros((H, W, 3), np.float32)
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(-1, 1, W)[None, :]
    top = np.array([16, 14, 40]); bot = np.array([8, 10, 24])
    g[:] = (top * (1 - yy) + bot * yy)[..., None].transpose(0, 2, 1) if False else 0
    for c in range(3):
        g[..., c] = top[c] * (1 - yy) + bot[c] * yy
    glow = np.exp(-((xx) ** 2 * 2.2 + ((yy - 0.48) * 2.4) ** 2))
    g += glow[..., None] * np.array([38, 26, 90])
    img = Image.fromarray(np.clip(g, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(img)
    rnd = random.Random(5)
    for _ in range(140):
        x, y = rnd.randrange(W), rnd.randrange(H); r = rnd.choice([1, 1, 1, 2])
        a = rnd.randrange(60, 170); d.ellipse((x - r, y - r, x + r, y + r), fill=(a, a, a + 20))
    # faint half court at the feet
    court = Image.new('L', (W, H), 0); cd = ImageDraw.Draw(court)
    cd.arc((140, 1560, 940, 2160), 180, 360, fill=70, width=4)
    cd.line((40, 1700, 1040, 1700), fill=40, width=3)
    img.paste((120, 100, 220), (0, 0), court)
    # the player
    m = Image.new('L', (W, H), 0); md = ImageDraw.Draw(m)
    md.ellipse((540 - 78, 560, 540 + 78, 716), fill=255)                 # head
    md.rectangle((515, 700, 565, 760), fill=255)                         # neck
    md.rounded_rectangle((392, 752, 688, 1200), radius=70, fill=255)     # body
    def limb(p, q, w):
        dx, dy = q[0] - p[0], q[1] - p[1]; L = math.hypot(dx, dy); nx, ny = -dy / L * w / 2, dx / L * w / 2
        md.polygon([(p[0] + nx, p[1] + ny), (q[0] + nx, q[1] + ny), (q[0] - nx, q[1] - ny), (p[0] - nx, p[1] - ny)], fill=255)
        md.ellipse((q[0] - w / 2, q[1] - w / 2, q[0] + w / 2, q[1] + w / 2), fill=255)
    limb((420, 800), (330, 1150), 74); limb((660, 800), (750, 1150), 74)   # arms
    md.rectangle((410, 1150, 528, 1640), fill=255); md.rectangle((552, 1150, 670, 1640), fill=255)  # legs
    m = m.filter(ImageFilter.GaussianBlur(2))
    m = m.point(lambda v: 255 if v > 128 else 0)
    edge = m.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.MaxFilter(5))
    fill = Image.new('RGB', (W, H), (14, 12, 34))
    img.paste(fill, (0, 0), m)
    # jersey number, faint
    jn = Image.new('L', (W, H), 0); ImageDraw.Draw(jn).text((540, 960), '23', font=anton(190), fill=34, anchor='mm')
    img.paste((140, 120, 255), (0, 0), jn)
    gl = Image.new('RGB', (W, H), 0); gl.paste(NEON, (0, 0), edge)
    big = gl.filter(ImageFilter.GaussianBlur(18))
    img = Image.fromarray(np.clip(np.asarray(img, np.int16) + np.asarray(big, np.int16) * 1.6, 0, 255).astype(np.uint8))
    img.paste((200, 180, 255), (0, 0), edge.filter(ImageFilter.MinFilter(3)))
    return img

# ── ball sprites ──
def ball_sprite(r, hot=False):
    pad = 70; s = 2 * (r + pad)
    im = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    gl = Image.new('RGBA', (s, s), (0, 0, 0, 0)); ImageDraw.Draw(gl).ellipse((pad - 14, pad - 14, s - pad + 14, s - pad + 14), fill=(255, 140, 40, 150) if not hot else (255, 60, 60, 190))
    im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(22)))
    b = Image.new('RGBA', (s, s), (0, 0, 0, 0)); bd = ImageDraw.Draw(b)
    c = s / 2
    # shaded orange sphere
    for k in range(r, 0, -1):
        f = k / r
        col = (int(150 + 105 * (1 - f) ** 0.7), int(55 + 70 * (1 - f) ** 0.8), int(10 + 20 * (1 - f)))
        ox, oy = -r * 0.28 * (1 - f), -r * 0.30 * (1 - f)
        bd.ellipse((c + ox - k, c + oy - k, c + ox + k, c + oy + k), fill=col + (255,))
    # seams
    lw = max(3, r // 11); sc = (40, 18, 8, 255)
    bd.line((c - r, c, c + r, c), fill=sc, width=lw)
    bd.line((c, c - r, c, c + r), fill=sc, width=lw)
    bd.arc((c - r * 1.55, c - r, c - r * 0.35, c + r), -62, 62, fill=sc, width=lw)
    bd.arc((c + r * 0.35, c - r, c + r * 1.55, c + r), 118, 242, fill=sc, width=lw)
    mask = Image.new('L', (s, s), 0); ImageDraw.Draw(mask).ellipse((c - r, c - r, c + r, c + r), fill=255)
    b.putalpha(mask)
    hl = Image.new('RGBA', (s, s), (0, 0, 0, 0)); ImageDraw.Draw(hl).ellipse((c - r * 0.6, c - r * 0.75, c - r * 0.05, c - r * 0.35), fill=(255, 255, 255, 90))
    b.alpha_composite(hl.filter(ImageFilter.GaussianBlur(6)))
    im.alpha_composite(b)
    return im

R = 62
BALL = ball_sprite(R); BALL_HOT = ball_sprite(R, True)

def paste_c(img, spr, x, y, a=1.0, scale=1.0):
    if scale != 1.0:
        w = max(2, int(spr.width * scale)); spr = spr.resize((w, w), Image.LANCZOS)
    if a < 1.0:
        al = spr.getchannel('A').point(lambda v: int(v * a)); spr = spr.copy(); spr.putalpha(al)
    img.alpha_composite(spr, (int(x - spr.width / 2), int(y - spr.height / 2)))

def ease(u): u = min(1, max(0, u)); return 1 - (1 - u) ** 3
def pop(u):
    u = min(1, max(0, u)); return 1 + 0.18 * math.sin(u * math.pi) if u < 1 else 1

def text_c(d, xy, s, font, fill, stroke=0, sf=(0, 0, 0)):
    d.text(xy, s, font=font, fill=fill, anchor='mm', stroke_width=stroke, stroke_fill=sf)

def pill(img, cx, cy, s, font, bg, fg):
    d = ImageDraw.Draw(img); bb = d.textbbox((0, 0), s, font=font)
    w, h = bb[2] - bb[0] + 56, bb[3] - bb[1] + 30
    d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), radius=h / 2, fill=bg)
    text_c(d, (cx, cy), s, font, fg)

def title(img, a):
    """¿PUEDES SEGUIR / EL BALÓN?  — slides down and fades in"""
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    f = anton(118); y0 = 205 - 40 * (1 - a)
    text_c(d, (540, y0), '¿PUEDES SEGUIR', f, WHITE)
    # second line: "EL" white + "BALÓN?" orange
    w1 = d.textlength('EL ', font=f); w2 = d.textlength('BALÓN?', font=f); x = 540 - (w1 + w2) / 2
    d.text((x, y0 + 128), 'EL ', font=f, fill=WHITE, anchor='lm'); d.text((x + w1, y0 + 128), 'BALÓN?', font=f, fill=ORANGE, anchor='lm')
    if a < 1: lay.putalpha(lay.getchannel('A').point(lambda v: int(v * a)))
    img.alpha_composite(lay)

def bottom(img, s, a=1.0, col=WHITE, size=64, y=1810):
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    text_c(d, (540, y), s, outfit(size), col)
    if a < 1: lay.putalpha(lay.getchannel('A').point(lambda v: int(v * a)))
    img.alpha_composite(lay)

BG = None
def frame(tt):
    img = BG.copy().convert('RGBA')
    d = ImageDraw.Draw(img)
    title(img, ease(tt / 0.3))
    if tt < T_BRAND:
        pill(img, 540, 82, 'TEST DE ATENCIÓN', outfit(34, 800), (120, 230, 120), (14, 30, 14))
    pos, moving = positions_at(tt)
    # balls appear one by one
    for k in range(3):
        appear = ease((tt - 0.05 - 0.08 * k) / 0.25)
        if appear <= 0: continue
        x, y = pos[k]
        hot = (k == 0 and T_SHOW <= tt < T_HIDE)
        sc = (0.5 + 0.5 * appear) * (pop((tt - T_SHOW) / 0.35) if hot else 1)
        paste_c(img, BALL_HOT if hot else BALL, x, y, appear, sc)
    # "this one": red ring + arrow label, pulsing
    if T_SHOW <= tt < T_HIDE:
        x, y = SPOTS[0]; ph = (tt - T_SHOW)
        rr = R + 18 + 8 * math.sin(ph * 7)
        d = ImageDraw.Draw(img)
        d.ellipse((x - rr, y - rr, x + rr, y + rr), outline=RED, width=7)
        a = ease(ph / 0.3) * (1 - ease((tt - (T_HIDE - 0.3)) / 0.3))
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        ld.rounded_rectangle((x + 100, y - 46, x + 430, y + 46), radius=46, fill=(255, 70, 70, 235))
        ld.polygon([(x + 84, y), (x + 108, y - 18), (x + 108, y + 18)], fill=(255, 70, 70, 235))
        text_c(ld, (x + 265, y + 2), 'SIGUE ESTE', outfit(44, 800), WHITE)
        lay.putalpha(lay.getchannel('A').point(lambda v: int(v * a))); img.alpha_composite(lay)
    # words at the bottom
    if T_SHOW <= tt < T_HIDE:
        bottom(img, 'Mira bien cuál es...', ease((tt - T_SHOW) / 0.3))
    elif T_HIDE <= tt < swaps[0][0] + 1.2:
        bottom(img, '¡No lo pierdas de vista!', ease((tt - T_HIDE) / 0.25), GOLD)
    elif swaps[0][0] + 1.2 <= tt < T_STOP:
        k = int((tt - swaps[0][0]) * 2) % 2
        bottom(img, 'Concéntrate...' if tt < (swaps[0][0] + T_STOP) / 2 else '¡Más rápido!', 1.0, WHITE if tt < (swaps[0][0] + T_STOP) / 2 else ORANGE)
    # the question
    if T_ASK <= tt < T_BRAND:
        u = ease((tt - T_ASK) / 0.35)
        d = ImageDraw.Draw(img)
        for i, (x, y) in enumerate(SPOTS):
            lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
            cx, cy = (x + R + 80, y) if i == 0 else (x, y + R + 70)     # the top one is labelled beside it, off the head
            ld.ellipse((cx - 46, cy - 46, cx + 46, cy + 46), fill=(255, 255, 255, 240))
            text_c(ld, (cx, cy + 3), str(i + 1), anton(64), (20, 16, 40))
            lay.putalpha(lay.getchannel('A').point(lambda v: int(v * u))); img.alpha_composite(lay)
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        ld.rounded_rectangle((90, 1700, 990, 1890), radius=40, fill=(10, 8, 26, 230), outline=(150, 110, 255, 255), width=3)
        text_c(ld, (540, 1758), '¿DÓNDE ESTÁ EL BALÓN?', anton(76), WHITE)
        text_c(ld, (540, 1840), 'Comenta 1, 2 o 3', outfit(50), GOLD)
        lay.putalpha(lay.getchannel('A').point(lambda v: int(v * u))); img.alpha_composite(lay)
        # countdown bar across the top of the box
        left = max(0, 1 - (tt - T_ASK - 0.4) / (T_END - T_ASK - 0.6))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((120, 1682, 120 + 840 * left, 1692), radius=5, fill=ORANGE)
    # end card
    if tt >= T_BRAND:
        u = ease((tt - T_BRAND) / 0.4)
        lay = Image.new('RGBA', (W, H), (8, 8, 20, int(215 * u))); ld = ImageDraw.Draw(lay)
        a = int(255 * u)
        text_c(ld, (540, 860), 'COGNITIVO GYM', anton(130), ORANGE + (a,))
        text_c(ld, (540, 990), 'Entrena tu mente como entrenas tu juego', outfit(46, 600), (230, 230, 245, a))
        text_c(ld, (540, 1110), '¿Lo encontraste? Comenta tu número', outfit(46, 700), GOLD + (a,))
        img.alpha_composite(lay)
    return img.convert('RGB')

if __name__ == '__main__':
    BG = background()
    mode = sys.argv[1] if len(sys.argv) > 1 else 'preview'
    info = {'duration': round(DUR, 2), 'answer': final_spot() + 1, 'swaps': len(swaps), 't_stop': round(T_STOP, 2), 't_ask': round(T_ASK, 2),
            'swap_times': [(round(a, 3), round(b, 3)) for a, b, _ in swaps], 't_show': T_SHOW, 't_hide': T_HIDE, 't_brand': round(T_BRAND, 2)}
    json.dump(info, open(OUT + '/info.json', 'w'))
    print(info['duration'], 'answer', info['answer'])
    if mode == 'preview':
        for tt in [0.3, 0.8, 3.3, 8.0, T_ASK + 1.5, T_BRAND + 1.2]:
            frame(tt).save(OUT + '/p-%05.2f.png' % tt)
    else:
        tmp = OUT + '/video.tmp.mp4'
        p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '%dx%d' % (W, H), '-r', str(FPS), '-i', '-',
                              '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', tmp], stdin=subprocess.PIPE)
        n = int(DUR * FPS)
        for i in range(n):
            p.stdin.write(frame(i / FPS).tobytes())
        p.stdin.close(); p.wait()
        if p.returncode == 0: os.replace(tmp, OUT + '/video.mp4')   # silent; build.sh adds the music
        print('done', p.returncode)
