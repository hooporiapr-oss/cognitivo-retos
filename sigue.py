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
BEBAS = os.path.join(HERE, 'BebasNeue.woff')
def bebas(n): return ImageFont.truetype(BEBAS, n)

ORANGE = (255, 122, 24); NEON = (150, 110, 255); CYAN = (90, 230, 255); WHITE = (255, 255, 255)
GREEN = (120, 230, 120); RED = (255, 70, 70); GOLD = (255, 205, 60)
# Cognitivo Gym's own colours (the same as the gym's site)
CG_GOLD = (255, 215, 0); CG_ORANGE = (255, 107, 53); CG_DARK = (10, 10, 15); CG_MUTED = (136, 146, 160)

# ── the three spots: above the head, left hand, right hand ──
# ── a regulation (FIBA) half court, 80 px per metre, baseline at the bottom ──
PX = 80.0
BASE_Y = 1800                                   # baseline
MID_Y = BASE_Y - 14.0 * PX                      # half-court line (14 m)
HOOP = (540, BASE_Y - 1.575 * PX)               # centre of the rim
FT_Y = BASE_Y - 5.8 * PX                        # free-throw line
LANE = 4.9 * PX / 2                             # half the lane's width
# the three spots: the centre circle and the two elbows
SPOTS = [(540, int(MID_Y)), (int(540 - LANE), int(FT_Y)), (int(540 + LANE), int(FT_Y))]
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

# ── static background: a perfect Cognitivo Gym court, seen from above ──
def background(piso='COGNITIVO GYM'):
    """piso: the words painted on the floor (a team version puts its own name)"""
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(-1, 1, W)[None, :]
    g = np.zeros((H, W, 3), np.float32) + np.array(CG_DARK, np.float32)
    # glossy dark hardwood: boards along the length, with staggered joints
    rnd = random.Random(7); bw = 40
    for i in range(W // bw + 1):
        x0 = i * bw; tone = rnd.uniform(0.85, 1.15)
        g[:, x0:x0 + bw] += np.array([20, 13, 7], np.float32) * tone
        g[:, x0:x0 + 2] *= 0.55                                           # seam between boards
        y = rnd.randrange(0, 400)
        while y < H: g[y:y + 2, x0:x0 + bw] *= 0.6; y += rnd.randrange(380, 620)
    # spotlight on the court and a soft sheen down the middle
    spot = np.exp(-((xx) ** 2 * 1.3 + ((yy - 0.6) * 1.7) ** 2))
    g *= (0.55 + 0.9 * spot)[..., None]
    g += (np.exp(-(xx * 3.2) ** 2) * np.exp(-((yy - 0.55) * 2.5) ** 2) * 26)[..., None] * np.array([1, 0.8, 0.5])
    img = Image.fromarray(np.clip(g, 0, 255).astype(np.uint8)).convert('RGBA')
    gw = (CG_GOLD[0], CG_GOLD[1], CG_GOLD[2])
    def grad_fill(mask, alpha):
        u = np.clip(yy * 1.0, 0, 1)[..., None]
        col = np.array(CG_ORANGE, np.float32) * u + np.array(CG_GOLD, np.float32) * (1 - u)
        f = Image.fromarray(np.repeat(col, W, 1).astype(np.uint8))
        img.alpha_composite(Image.merge('RGBA', (*f.split(), mask.point(lambda v: int(v * alpha)))))
    # painted areas: the lane and the centre circle, in the gym's gold-to-orange
    pm = Image.new('L', (W, H), 0); pd = ImageDraw.Draw(pm)
    pd.rectangle((540 - LANE, FT_Y, 540 + LANE, BASE_Y), fill=255)
    pd.ellipse((540 - 1.8 * PX, MID_Y - 1.8 * PX, 540 + 1.8 * PX, MID_Y + 1.8 * PX), fill=255)
    grad_fill(pm, 0.30)
    # the lines, exactly where FIBA puts them
    m = Image.new('L', (W, H), 0); d = ImageDraw.Draw(m); lw = 8
    d.line((0, MID_Y, W, MID_Y), fill=255, width=lw)                                        # half-court line
    d.ellipse((540 - 1.8 * PX, MID_Y - 1.8 * PX, 540 + 1.8 * PX, MID_Y + 1.8 * PX), outline=255, width=lw)
    d.line((0, BASE_Y, W, BASE_Y), fill=255, width=lw)                                      # baseline
    d.rectangle((540 - LANE, FT_Y, 540 + LANE, BASE_Y), outline=255, width=lw)              # the lane
    d.ellipse((540 - 1.8 * PX, FT_Y - 1.8 * PX, 540 + 1.8 * PX, FT_Y + 1.8 * PX), outline=255, width=lw)  # free-throw circle
    for k in range(1, 4):                                                                   # lane hash marks
        for sx in (-1, 1):
            y = BASE_Y - (1.75 + k * 0.85) * PX; x = 540 + sx * LANE
            d.line((x, y, x + sx * 0.1 * PX * 2.2, y), fill=255, width=lw - 2)
    r3 = 6.75 * PX; cx3 = 540 - 0.9 * PX * 0 ; side = 540 - 0.9 * PX                       # 3-pt: 6.75 m, corners 0.9 m in
    dx = 540 - 0.9 * PX; ang = math.degrees(math.asin(min(1, (W / 2 - 0.9 * PX * 0 - 12) / r3)))
    xc = r3 * math.sin(math.radians(ang)); yc = HOOP[1] - r3 * math.cos(math.radians(ang))
    d.arc((HOOP[0] - r3, HOOP[1] - r3, HOOP[0] + r3, HOOP[1] + r3), 270 - ang, 270 + ang, fill=255, width=lw)
    for sx in (-1, 1): d.line((HOOP[0] + sx * xc, yc, HOOP[0] + sx * xc, BASE_Y), fill=255, width=lw)
    d.arc((HOOP[0] - 1.25 * PX, HOOP[1] - 1.25 * PX, HOOP[0] + 1.25 * PX, HOOP[1] + 1.25 * PX), 180, 360, fill=255, width=lw - 2)  # no-charge arc
    lines = Image.new('RGB', (W, H), gw)
    wide = Image.new('RGBA', (W, H), CG_ORANGE + (0,)); wide.putalpha(m.filter(ImageFilter.GaussianBlur(26)).point(lambda v: min(255, int(v * 1.6))))
    near = Image.new('RGBA', (W, H), CG_GOLD + (0,)); near.putalpha(m.filter(ImageFilter.GaussianBlur(7)).point(lambda v: min(255, int(v * 1.5))))
    img.alpha_composite(wide); img.alpha_composite(near)
    core = Image.new('RGBA', (W, H), (255, 244, 190, 0)); core.putalpha(m); img.alpha_composite(core)
    # backboard and rim, glowing orange
    hb = Image.new('RGBA', (W, H), (0, 0, 0, 0)); hd = ImageDraw.Draw(hb)
    hd.line((540 - 0.9 * PX, BASE_Y - 1.2 * PX, 540 + 0.9 * PX, BASE_Y - 1.2 * PX), fill=(255, 255, 255, 255), width=10)
    hd.ellipse((HOOP[0] - 0.23 * PX, HOOP[1] - 0.23 * PX, HOOP[0] + 0.23 * PX, HOOP[1] + 0.23 * PX), outline=CG_ORANGE + (255,), width=7)
    img.alpha_composite(hb.filter(ImageFilter.GaussianBlur(8))); img.alpha_composite(hb)
    # centre-court logo
    # COGNITIVO GYM painted on the floor, between the centre circle and the arc
    cg = Image.new('RGBA', (W, H), (0, 0, 0, 0)); cd = ImageDraw.Draw(cg); f = bebas(110); t = piso
    ws = [cd.textlength(c, font=f) for c in t]; sp = 14; x = 540 - (sum(ws) + sp * (len(t) - 1)) / 2
    for c, w in zip(t, ws): cd.text((x, (MID_Y + 1.8 * PX + HOOP[1] - r3) / 2), c, font=f, fill=(255, 225, 150, 52), anchor='lm'); x += w + sp
    img.alpha_composite(cg)
    # dark band behind the title so it always reads
    top = np.clip(1 - yy / 0.24, 0, 1) ** 1.6
    shade = Image.fromarray((np.repeat(top * 200, W, 1)).astype(np.uint8))
    img.alpha_composite(Image.merge('RGBA', (*Image.new('RGB', (W, H), CG_DARK).split(), shade)))
    return img.convert('RGB')

def grad_text(img, xy, s, font, a=1.0, spacing=0, anchor='mm'):
    """text filled gold to orange, left to right, like the gym's wordmark"""
    lay = Image.new('L', (W, H), 0); d = ImageDraw.Draw(lay)
    if spacing:
        ws = [d.textlength(c, font=font) for c in s]; tot = sum(ws) + spacing * (len(s) - 1)
        x = xy[0] - tot / 2
        for c, w in zip(s, ws): d.text((x, xy[1]), c, font=font, fill=255, anchor='lm'); x += w + spacing
    else:
        d.text(xy, s, font=font, fill=255, anchor=anchor)
    bb = lay.getbbox()
    if not bb: return
    x0, x1 = bb[0], max(bb[2], bb[0] + 1)
    u = np.clip((np.arange(W) - x0) / (x1 - x0), 0, 1)[None, :, None]
    col = np.array(CG_GOLD, np.float32) * (1 - u) + np.array(CG_ORANGE, np.float32) * u
    fill = Image.fromarray(np.repeat(col, H, 0).astype(np.uint8))
    al = lay.point(lambda v: int(v * a))
    img.paste(fill, (0, 0), al) if img.mode == 'RGB' else img.alpha_composite(Image.merge('RGBA', (*fill.split(), al)))

def wordmark(img, y=74, a=1.0):
    """COGNITIVO GYM, spaced, gold to orange — the top of every frame"""
    grad_text(img, (540, y), 'COGNITIVO GYM', bebas(64), a, spacing=10)

def endcard(img, u, line):
    """the closing card, laid out like the gym's own start screen"""
    lay = Image.new('RGBA', (W, H), CG_DARK + (int(235 * u),)); img.alpha_composite(lay)
    a = u
    grad_text(img, (540, 770), 'COGNITIVO', bebas(190), a, spacing=16)
    grad_text(img, (540, 930), 'GYM', bebas(190), a, spacing=16)
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay); al = int(255 * a)
    t = 'CADA PUNTO CUENTA'; f = outfit(36, 700); ws = [ld.textlength(c, font=f) for c in t]; sp = 11; x = 540 - (sum(ws) + sp * (len(t) - 1)) / 2
    for c, w in zip(t, ws): ld.text((x, 1048), c, font=f, fill=CG_MUTED + (al,), anchor='lm'); x += w + sp
    img.alpha_composite(lay)
    # the gradient button: where to play
    bt = Image.new('RGBA', (W, H), (0, 0, 0, 0)); bd = ImageDraw.Draw(bt)
    m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).rounded_rectangle((150, 1140, 930, 1280), radius=26, fill=al)
    u2 = np.clip((np.arange(W) - 150) / 780, 0, 1)[None, :, None]
    col = np.array(CG_GOLD, np.float32) * (1 - u2) + np.array(CG_ORANGE, np.float32) * u2
    fill = Image.fromarray(np.repeat(col, H, 0).astype(np.uint8))
    img.alpha_composite(Image.merge('RGBA', (*fill.split(), m)))
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    text_c(ld, (540, 1213), 'COGNOGYM.COM', bebas(84), (26, 15, 15, al))
    text_c(ld, (540, 1380), line, outfit(46, 700), (235, 235, 240, al))
    img.alpha_composite(lay)

def endcard_brillante(img, u, line):
    """A brighter closing card (Nov 2026), used by the ¿Quién tiene el balón?
    videos: the court stays visible behind a lighter veil, a warm gold
    spotlight sits behind the wordmark, and the wordmark and button glow."""
    img.alpha_composite(Image.new('RGBA', (W, H), CG_DARK + (int(178 * u),)))
    yy = np.linspace(0, 1, H)[:, None]; xx = np.linspace(-1, 1, W)[None, :]
    luz = np.exp(-(xx ** 2 * 1.4 + ((yy - 0.48) * 3.0) ** 2))
    glow = np.zeros((H, W, 4), np.float32)
    glow[..., :3] = np.array([255, 120, 40], np.float32) * (1 - luz[..., None] * 0.35) + np.array([255, 200, 120], np.float32) * luz[..., None] * 0.35   # warm orange, lighter at the centre
    glow[..., 3] = luz * 105 * u
    img.alpha_composite(Image.fromarray(glow.astype(np.uint8), 'RGBA'))
    # the wordmark, with a soft halo behind it
    halo = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    grad_text(halo, (540, 770), 'COGNITIVO', bebas(190), u, spacing=16); grad_text(halo, (540, 930), 'GYM', bebas(190), u, spacing=16)
    img.alpha_composite(halo.filter(ImageFilter.GaussianBlur(22))); img.alpha_composite(halo)
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay); al = int(255 * u)
    t = 'CADA PUNTO CUENTA'; f = outfit(38, 800); ws = [ld.textlength(c, font=f) for c in t]; sp = 11; x = 540 - (sum(ws) + sp * (len(t) - 1)) / 2
    for c, w in zip(t, ws): ld.text((x, 1048), c, font=f, fill=(255, 255, 255, al), anchor='lm'); x += w + sp
    img.alpha_composite(lay)
    # the button, glowing
    m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).rounded_rectangle((150, 1140, 930, 1280), radius=26, fill=al)
    u2 = np.clip((np.arange(W) - 150) / 780, 0, 1)[None, :, None]
    col = np.array(CG_GOLD, np.float32) * (1 - u2) + np.array(CG_ORANGE, np.float32) * u2
    fill = Image.fromarray(np.repeat(col, H, 0).astype(np.uint8))
    btn = Image.merge('RGBA', (*fill.split(), m))
    img.alpha_composite(btn.filter(ImageFilter.GaussianBlur(24))); img.alpha_composite(btn)
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    text_c(ld, (540, 1213), 'COGNOGYM.COM', bebas(84), (26, 15, 15, al))
    tw = ld.textlength(line, font=outfit(46, 700))
    ld.rounded_rectangle((540 - tw / 2 - 36, 1334, 540 + tw / 2 + 36, 1426), radius=46, fill=CG_DARK + (int(200 * u),))
    text_c(ld, (540, 1380), line, outfit(46, 700), (255, 255, 255, al))
    img.alpha_composite(lay)

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

def title(img, a, l1='¿PUEDES SEGUIR', l2a='EL ', l2b='BALÓN?'):
    """two-line title in the gym's Bebas Neue: white, then the key word in gold to orange"""
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    f = bebas(150); y0 = 190 - 40 * (1 - a)
    text_c(d, (540, y0), l1, f, WHITE)
    w1 = d.textlength(l2a, font=f); w2 = d.textlength(l2b, font=f); x = 540 - (w1 + w2) / 2
    d.text((x, y0 + 132), l2a, font=f, fill=WHITE, anchor='lm')
    if a < 1: lay.putalpha(lay.getchannel('A').point(lambda v: int(v * a)))
    img.alpha_composite(lay)
    grad_text(img, (x + w1, y0 + 132), l2b, f, a, anchor='lm')

def bottom(img, s, a=1.0, col=WHITE, size=64, y=1810):
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    tw = d.textlength(s, font=outfit(size))
    d.rounded_rectangle((540 - tw / 2 - 40, y - 52, 540 + tw / 2 + 40, y + 50), radius=50, fill=CG_DARK + (225,))   # so it reads over the court lines
    text_c(d, (540, y), s, outfit(size), col)
    if a < 1: lay.putalpha(lay.getchannel('A').point(lambda v: int(v * a)))
    img.alpha_composite(lay)

BG = None
def frame(tt):
    img = BG.copy().convert('RGBA')
    d = ImageDraw.Draw(img)
    if tt < T_BRAND:
        wordmark(img)
    title(img, ease(tt / 0.3))
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
        bottom(img, '¡No lo pierdas de vista!', ease((tt - T_HIDE) / 0.25), CG_GOLD)
    elif swaps[0][0] + 1.2 <= tt < T_STOP:
        k = int((tt - swaps[0][0]) * 2) % 2
        bottom(img, 'Concéntrate...' if tt < (swaps[0][0] + T_STOP) / 2 else '¡Más rápido!', 1.0, WHITE if tt < (swaps[0][0] + T_STOP) / 2 else CG_ORANGE)
    # the question
    if T_ASK <= tt < T_BRAND:
        u = ease((tt - T_ASK) / 0.35)
        d = ImageDraw.Draw(img)
        for i, (x, y) in enumerate(SPOTS):
            lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
            cx, cy = (x + R + 80, y) if i == 0 else (x, y + R + 70)     # the top one is labelled beside it, off the head
            ld.ellipse((cx - 46, cy - 46, cx + 46, cy + 46), fill=CG_GOLD + (245,))
            text_c(ld, (cx, cy + 4), str(i + 1), bebas(80), (26, 15, 15))
            lay.putalpha(lay.getchannel('A').point(lambda v: int(v * u))); img.alpha_composite(lay)
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        ld.rounded_rectangle((90, 1700, 990, 1890), radius=26, fill=CG_DARK + (238,), outline=CG_GOLD + (255,), width=4)
        text_c(ld, (540, 1760), '¿DÓNDE ESTÁ EL BALÓN?', bebas(96), WHITE)
        text_c(ld, (540, 1846), 'Comenta 1, 2 o 3', outfit(50), CG_GOLD)
        lay.putalpha(lay.getchannel('A').point(lambda v: int(v * u))); img.alpha_composite(lay)
        # countdown bar across the top of the box
        left = max(0, 1 - (tt - T_ASK - 0.4) / (T_END - T_ASK - 0.6))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((120, 1682, 120 + 840 * left, 1692), radius=5, fill=CG_ORANGE)
    # end card
    if tt >= T_BRAND:
        endcard(img, ease((tt - T_BRAND) / 0.4), '¿Lo encontraste? Comenta tu número')
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
