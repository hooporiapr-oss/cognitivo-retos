# The answer video for "¿Puedes seguir el balón?": the same 18 swaps from
# sigue.py, slowed down, with the ball to follow kept red and leaving a
# trail, ending on "¡ERA EL 2!".  python3 respuesta.py preview|render
import sys, os, math, json, subprocess
from PIL import Image, ImageDraw
import sigue as G

SLOW = 0.62                      # game seconds per video second during the swaps
T0 = 1.6                         # video time when the first swap starts
G0 = G.swaps[0][0]               # game time of the first swap
def g_of(tt):                    # video time -> game time
    if tt < T0: return G0 - 0.01
    return G0 + (tt - T0) * SLOW
T_STOP = T0 + (G.T_STOP - G0) / SLOW
T_ROLL = T_STOP + 0.3
T_REVEAL = T_ROLL + 1.3
T_BRAND = T_REVEAL + 3.2
DUR = T_BRAND + 2.4
ANS = G.final_spot()             # 0-based spot index

def frame(tt):
    img = G.BG.copy().convert('RGBA'); d = ImageDraw.Draw(img)
    # wordmark, then the title: ¿LO SEGUISTE? / MÍRALO OTRA VEZ
    if tt < T_BRAND:
        G.wordmark(img)
    G.title(img, G.ease(tt / 0.3), '¿LO SEGUISTE?', 'MÍRALO ', 'OTRA VEZ')
    g = g_of(tt) if tt < T_STOP else G.T_STOP
    pos, moving = G.positions_at(g)
    # the trail of the ball to follow
    if T0 <= tt < T_STOP + 0.4:
        for i in range(14, 0, -1):
            p, _ = G.positions_at(max(G0, g - i * 0.035))
            r = 26 - i * 1.4; al = int(150 * (1 - i / 15))
            tl = Image.new('RGBA', (G.W, G.H), (0, 0, 0, 0))
            ImageDraw.Draw(tl).ellipse((p[0][0] - r, p[0][1] - r, p[0][0] + r, p[0][1] + r), fill=(255, 70, 70, al))
            img.alpha_composite(tl)
    for k in (1, 2, 0):          # the red one drawn last, always on top
        x, y = pos[k]
        G.paste_c(img, G.BALL_HOT if k == 0 else G.BALL, x, y, 1.0 if k == 0 else 0.55)
    x, y = pos[0]; rr = G.R + 16 + 6 * math.sin(tt * 7)
    ImageDraw.Draw(img).ellipse((x - rr, y - rr, x + rr, y + rr), outline=G.RED, width=7)
    # bottom words
    if tt < T0:
        G.bottom(img, 'Este es el balón', G.ease((tt - 0.2) / 0.3))
    elif tt < T_STOP:
        G.bottom(img, 'En cámara lenta...', 1.0, G.CG_GOLD)
    # the answer
    if tt >= T_ROLL:
        u = G.ease((tt - T_ROLL) / 0.3)
        for i, (sx, sy) in enumerate(G.SPOTS):
            lay = Image.new('RGBA', (G.W, G.H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
            cx, cy = (sx + G.R + 80, sy) if i == 0 else (sx, sy + G.R + 70)
            win = (i == ANS and tt >= T_REVEAL)
            sc = G.pop((tt - T_REVEAL) / 0.4) if win else 1
            rad = 46 * sc
            ld.ellipse((cx - rad, cy - rad, cx + rad, cy + rad), fill=(255, 70, 70, 255) if win else G.CG_GOLD + (245,))
            G.text_c(ld, (cx, cy + 4), str(i + 1), G.bebas(int(80 * sc)), G.WHITE if win else (26, 15, 15))
            lay.putalpha(lay.getchannel('A').point(lambda v: int(v * u))); img.alpha_composite(lay)
    if tt >= T_REVEAL and tt < T_BRAND:
        u = G.ease((tt - T_REVEAL) / 0.3); sc = G.pop((tt - T_REVEAL) / 0.4)
        lay = Image.new('RGBA', (G.W, G.H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        ld.rounded_rectangle((90, 1700, 990, 1890), radius=26, fill=G.CG_DARK + (238,), outline=(255, 70, 70, 255), width=4)
        G.text_c(ld, (540, 1762), '¡ERA EL ' + str(ANS + 1) + '!', G.bebas(int(118 * sc)), G.WHITE)
        G.text_c(ld, (540, 1850), '¿Acertaste? Cuéntanos', G.outfit(48), G.CG_GOLD)
        lay.putalpha(lay.getchannel('A').point(lambda v: int(v * u))); img.alpha_composite(lay)
    elif T_ROLL <= tt < T_REVEAL:
        G.bottom(img, 'La respuesta es...', G.ease((tt - T_ROLL) / 0.25), G.WHITE, 66)
    if tt >= T_BRAND:
        G.endcard(img, G.ease((tt - T_BRAND) / 0.4), 'Un reto nuevo cada semana')
    return img.convert('RGB')

if __name__ == '__main__':
    G.BG = G.background()
    info = {'duration': round(DUR, 2), 't_show': 0.0, 't_hide': T0, 't_stop': round(T_STOP, 3), 't_ask': round(T_ROLL, 3),
            't_reveal': round(T_REVEAL, 3), 't_brand': round(T_BRAND, 3),
            'swap_times': [(round(T0 + (a - G0) / SLOW, 3), round(T0 + (b - G0) / SLOW, 3)) for a, b, _ in G.swaps]}
    json.dump(info, open('info-respuesta.json', 'w')); print(info['duration'], 'answer', ANS + 1)
    if sys.argv[1] == 'preview':
        for tt in [0.8, 5.0, T_STOP + 0.1, T_REVEAL + 0.8]:
            frame(tt).save('r-%05.2f.png' % tt)
    else:
        tmp = 'respuesta-video.tmp.mp4'
        p = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1080x1920', '-r', '30', '-i', '-',
                              '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', tmp], stdin=subprocess.PIPE)
        for i in range(int(DUR * 30)): p.stdin.write(frame(i / 30).tobytes())
        p.stdin.close(); p.wait()
        if p.returncode == 0: os.replace(tmp, 'respuesta-video.mp4')
        print('done', p.returncode)
