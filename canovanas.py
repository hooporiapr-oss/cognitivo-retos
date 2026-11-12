# "¿Quién tiene el balón? 5 balones" for CANÓVANAS BASKETBALL — the same
# game as cinco.py, dressed in the club's identity: navy and gold, their
# logo on top and on the closing card, their name painted on the floor,
# and standard basketball jersey numbers (4, 5, 10, 12, 15). Numbers only,
# never players' names. Its own pass plan, so its answer differs from the
# public 5 balones.
#   python3 canovanas.py reto preview|render       -> canovanas-video.mp4 (silent)
#   python3 canovanas.py respuesta preview|render  -> canovanas-respuesta-video.mp4
import os, sys
os.environ.setdefault('CINCO_SEED', '9')
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import sigue as G

# ── the club's colours, read off their logo ──
NAVY = (46, 38, 92); GOLD = (236, 180, 92); NAVY_DARK = (12, 10, 34)
G.CG_GOLD = GOLD                    # court lines, rings, highlights
G.CG_ORANGE = (255, 214, 140)       # the light end of every gold gradient
G.CG_DARK = NAVY_DARK

import quien as Q                   # imported after the colours: its tokens are drawn now
import cinco as C

Q.NUMS[:] = ['4', '5', '10', '12', '15']
def token(num, hot=False, dim=False):
    TR = Q.TR; s = 2 * (TR + 60); im = Image.new('RGBA', (s, s), (0, 0, 0, 0)); c = s / 2
    ring = (255, 70, 70) if hot else GOLD
    gl = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    ImageDraw.Draw(gl).ellipse((c - TR - 8, c - TR - 8, c + TR + 8, c + TR + 8), fill=ring + (40 if dim else 170,))
    im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(16)))
    d = ImageDraw.Draw(im)
    d.ellipse((c - TR, c - TR, c + TR, c + TR), fill=(255, 70, 70, 255) if hot else NAVY + (255,), outline=ring + (255,), width=8)
    d.text((c, c + 4), num, font=G.bebas(104), fill=(255, 255, 255, 255), anchor='mm')
    if dim: im.putalpha(im.getchannel('A').point(lambda v: int(v * 0.35)))
    return im
Q.TOK = [token(n) for n in Q.NUMS]; Q.TOK_DIM = [token(n, dim=True) for n in Q.NUMS]; Q.TOK_HOT = [token(n, True) for n in Q.NUMS]

LOGO = Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'canovanas', 'logo.png')).convert('RGBA')

def placa(img, cx, cy, w, a=1.0):
    """the logo on a white plate, so its navy reads on a dark court"""
    lg = LOGO.resize((int(w), int(w * LOGO.height / LOGO.width)), Image.LANCZOS)
    pw, ph = lg.width + 60, lg.height + 40
    lay = Image.new('RGBA', (G.W, G.H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((cx - pw / 2, cy - ph / 2, cx + pw / 2, cy + ph / 2), radius=26, fill=(255, 255, 255, 255), outline=GOLD + (255,), width=5)
    lay.alpha_composite(lg, (int(cx - lg.width / 2), int(cy - lg.height / 2)))
    if a < 1: lay.putalpha(lay.getchannel('A').point(lambda v: int(v * a)))
    img.alpha_composite(lay)

def wordmark(img, y=74, a=1.0):
    placa(img, 540, 108, 300, a)

def title(img, a, l1='¿QUIÉN TIENE', l2a='EL ', l2b='BALÓN?'):
    """the usual two-line title, moved down to make room for the logo"""
    lay = Image.new('RGBA', (G.W, G.H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    f = G.bebas(120); y0 = 300 - 30 * (1 - a)
    G.text_c(d, (540, y0), l1, f, G.WHITE)
    w1 = d.textlength(l2a, font=f); w2 = d.textlength(l2b, font=f); x = 540 - (w1 + w2) / 2
    d.text((x, y0 + 108), l2a, font=f, fill=G.WHITE, anchor='lm')
    if a < 1: lay.putalpha(lay.getchannel('A').point(lambda v: int(v * a)))
    img.alpha_composite(lay)
    G.grad_text(img, (x + w1, y0 + 108), l2b, f, a, anchor='lm')

def endcard(img, u, line):
    img.alpha_composite(Image.new('RGBA', (G.W, G.H), NAVY_DARK + (int(240 * u),)))
    placa(img, 540, 760, 760, u)
    lay = Image.new('RGBA', (G.W, G.H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); al = int(255 * u)
    G.text_c(d, (540, 1120), line, G.outfit(50, 700), (240, 240, 245, al))
    G.text_c(d, (540, 1680), 'Hecho por Cognitivo Gym · cognogym.com', G.outfit(34, 600), GOLD + (al,))
    img.alpha_composite(lay)

G.wordmark, G.title, G.endcard = wordmark, title, endcard
G.endcard_brillante = endcard          # cinco.py calls the bright card; the club keeps its own

def cancha():
    """the club's court: the same court, its wood turned navy, its name on the floor"""
    bg = np.asarray(G.background('CANÓVANAS')).astype(np.float32)
    L = bg.mean(2, keepdims=True)
    keep = np.clip((L - 70) / 90, 0, 1)                 # bright lines stay gold
    navy = L * np.array([0.55, 0.5, 1.35]) + np.array([4, 3, 14])
    return Image.fromarray(np.clip(bg * keep + navy * (1 - keep), 0, 255).astype(np.uint8))

if __name__ == '__main__':
    modo = sys.argv[1]; acc = sys.argv[2] if len(sys.argv) > 2 else 'preview'
    G.BG = cancha(); Q.MODO = modo
    print('answer', Q.NUMS[C.FINAL], '· the followed ball moved', C.VECES, 'times in the shuffle')
    import json
    if modo == 'reto':
        json.dump({'duration': round(C.DUR, 2), 't_show': C.T_SHOW, 't_hide': C.T_HIDE, 't_stop': round(C.T_STOP, 3), 't_ask': round(C.T_ASK, 3),
                   't_brand': round(C.T_BRAND, 3), 'swap_times': [(round(a, 3), round(b, 3)) for a, b in C.BEATS]}, open('info-canovanas.json', 'w'))
        if acc == 'preview':
            for tt in [1.2, C.BEATS[3][1] + 0.2, C.T_MEZCLA + 2.0, C.T_ASK + 1.5, C.T_BRAND + 1.2]: C.frame_reto(tt).save('cv-%05.2f.png' % tt)
        else: Q.render(C.frame_reto, C.DUR, 'canovanas-video.mp4')
    else:
        json.dump({'duration': round(C.DUR_R, 2), 't_show': 0.0, 't_hide': C.T0, 't_stop': round(C.T_STOP_R, 3), 't_ask': round(C.T_ROLL_R, 3),
                   't_reveal': round(C.T_REVEAL_R, 3), 't_brand': round(C.T_BRAND_R, 3),
                   'swap_times': [(round(C.T0 + (a - C.G0) / C.SLOW, 3), round(C.T0 + (b - C.G0) / C.SLOW, 3)) for a, b in C.BEATS]}, open('info-canovanas-respuesta.json', 'w'))
        if acc == 'preview':
            for tt in [C.T0 + 3.0, C.T_REVEAL_R + 0.8, C.T_BRAND_R + 1.2]: C.frame_resp(tt).save('cvr-%05.2f.png' % tt)
        else: Q.render(C.frame_resp, C.DUR_R, 'canovanas-respuesta-video.mp4')
