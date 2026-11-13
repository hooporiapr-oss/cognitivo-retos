# El Debate del Día: the daily YouTube Short (1080x1920, 30 fps, 12 s).
#
#   python3 debate_short.py dia.json arte.jpg salida.mp4
#
# dia.json is one day's question: {"fecha","categoria","domingo","es",
# "opciones":[{"id","es"},...]}. The questions are not kept in this repo
# (it is public), so the json comes from the private question file.
#
#   0.0 - 3.2  the day's art, slow push-in, "EL DEBATE DEL DÍA" on top
#   3.2 - 9.0  art sinks into a dark backdrop; the question, then each answer
#   9.0 - 12   closing card: ¿TÚ QUÉ DICES? · VOTA EN COGNOGYM.COM/DEBATE
import sys, os, json, subprocess, textwrap, tempfile
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import sigue as G
from sigue import bebas, outfit, grad_text, wordmark, text_c, CG_GOLD, CG_ORANGE, CG_DARK, CG_MUTED

W, H, FPS, DUR = 1080, 1920, 30, 12.0
T_SWAP, T_Q, T_ANS, T_END = 3.2, 3.5, 4.5, 9.0
CAT = {'prefieres': '¿QUÉ PREFIERES?', 'harias': '¿QUÉ TÚ HARÍAS?', 'debate': 'EL GRAN DEBATE',
       'antes': 'ANTES VS. AHORA', 'razon': '¿QUIÉN TIENE LA RAZÓN?', 'fanatico': 'DECISIÓN DEL FANÁTICO'}
MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
DIAS = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo']

def ease(u): u = min(1, max(0, u)); return 1 - (1 - u) ** 3
def clamp(u): return min(1, max(0, u))

def wrap(d, s, font, width):
    words, lines, cur = s.split(), [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if d.textlength(t, font=font) <= width or not cur: cur = t
        else: lines.append(cur); cur = w
    lines.append(cur); return lines

def fit(d, s, size, width, maxl, fn=bebas):
    while True:
        f = fn(size); l = wrap(d, s, f, width)
        if len(l) <= maxl or size < 40: return f, l
        size -= 4

def main(dia_json, arte, salida):
    P = json.load(open(dia_json))
    y, m, dd = map(int, P['fecha'].split('-'))
    import datetime; wd = datetime.date(y, m, dd).weekday()
    fecha_txt = ('%s %d de %s' % (DIAS[wd], dd, MESES[m - 1])).upper()
    art = Image.open(arte).convert('RGB').resize((1080, 1350), Image.LANCZOS)
    # backdrop: the art blown up, blurred and darkened
    bg = art.resize((int(1920 * 0.8), 1920), Image.LANCZOS).crop(((int(1920 * .8) - W) // 2, 0, (int(1920 * .8) - W) // 2 + W, H)).filter(ImageFilter.GaussianBlur(28))
    bg = Image.blend(bg, Image.new('RGB', (W, H), CG_DARK), 0.72)
    base = Image.new('RGB', (W, H), CG_DARK)
    # a warm glow at the top of the art frame
    glow = Image.new('L', (W, H), 0); ImageDraw.Draw(glow).ellipse((90, -240, 990, 420), fill=120); glow = glow.filter(ImageFilter.GaussianBlur(90))
    base = Image.composite(Image.new('RGB', (W, H), (60, 36, 8)), base, glow)
    scratch = ImageDraw.Draw(Image.new('RGB', (10, 10)))
    qf, ql = fit(scratch, P['es'].upper(), 112, 940, 4)
    ops = P['opciones']; of = outfit(50 if len(ops) <= 3 else 44, 800)
    op_lines = [wrap(scratch, o['es'], of, 760) for o in ops]
    sunday = P.get('domingo')
    lh = qf.size * 0.98
    content = len(ql) * lh + 50 + sum(70 + 60 * len(x) + 26 for x in op_lines) + 110
    card_h = int(min(560, max(300, 1640 - 290 - 40 - content))); card_w = int(card_h * 0.8)
    BIG = (43, 268, 994, 1242); SMALL = (540 - card_w // 2, 290, card_w, card_h)
    Q_TOP = 290 + card_h + 40

    def frame(t):
        # 1) the art: big and pushing in, then it shrinks to a card above the question
        u = clamp(t / T_END); s = 1.0 + 0.08 * ease(u)
        swap = ease((t - T_SWAP) / 0.7)
        img = Image.blend(base, bg, swap)
        bw, bh = int(BIG[2] + (SMALL[2] - BIG[2]) * swap), int(BIG[3] + (SMALL[3] - BIG[3]) * swap)
        bx, by = int(BIG[0] + (SMALL[0] - BIG[0]) * swap), int(BIG[1] + (SMALL[1] - BIG[1]) * swap)
        aw, ah = int(bw * s), int(bh * s)
        a2 = art.resize((aw, ah), Image.BILINEAR).crop(((aw - bw) // 2, (ah - bh) // 2, (aw - bw) // 2 + bw, (ah - bh) // 2 + bh))
        box = Image.new('L', (bw, bh), 0); ImageDraw.Draw(box).rounded_rectangle((0, 0, bw - 1, bh - 1), radius=int(34 - 10 * swap), fill=255)
        if t < T_END + 0.6: img.paste(a2, (bx, by), box)
        img = img.convert('RGBA')
        fin = clamp(t / 0.6)
        if fin < 1: img.alpha_composite(Image.new('RGBA', (W, H), CG_DARK + (int(255 * (1 - fin)),)))
        # top: wordmark, title, date
        top_a = ease(t / 0.5) * (1 - ease((t - T_END) / 0.4))
        wordmark(img, 70, top_a)
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        text_c(ld, (540, 160), 'EL DEBATE DEL DÍA' if not sunday else 'EL GRAN DEBATE DEL DOMINGO', bebas(84 if not sunday else 70), (255, 255, 255, int(255 * top_a)))
        text_c(ld, (540, 228), fecha_txt, outfit(34, 700), CG_MUTED + (int(255 * top_a),))
        img.alpha_composite(lay)
        # 2) the question and the answers
        if T_Q - 0.1 < t < T_END + 0.5:
            out = 1 - ease((t - T_END) / 0.4)
            qa = ease((t - T_Q) / 0.45) * out
            lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
            y0 = Q_TOP + 30 * (1 - qa)
            for i, l in enumerate(ql): text_c(ld, (540, int(y0 + i * lh + lh / 2)), l, qf, (255, 255, 255, int(255 * qa)))
            yq = Q_TOP + len(ql) * lh + 50
            img.alpha_composite(lay)
            for k, (o, ls) in enumerate(zip(ops, op_lines)):
                ta = T_ANS + k * 0.6; pa = ease((t - ta) / 0.35) * out
                if pa <= 0: continue
                hgt = 70 + 60 * len(ls); x0, x1 = 90, 990; yy = int(yq + sum(70 + 60 * len(x) + 26 for x in op_lines[:k]))
                dx = int(80 * (1 - pa))
                lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
                ld.rounded_rectangle((x0 + dx, yy, x1 + dx, yy + hgt), radius=26, fill=(28, 28, 39, int(235 * pa)), outline=CG_GOLD + (int(255 * pa),), width=4)
                ld.ellipse((x0 + 26 + dx, yy + hgt // 2 - 38, x0 + 102 + dx, yy + hgt // 2 + 38), fill=CG_GOLD + (int(255 * pa),))
                text_c(ld, (x0 + 64 + dx, yy + hgt // 2 + 2), 'ABCD'[k], bebas(62), (26, 15, 15, int(255 * pa)))
                for i, l in enumerate(ls): ld.text((x0 + 132 + dx, yy + 35 + 60 * i + 30), l, font=of, fill=(255, 255, 255, int(255 * pa)), anchor='lm')
                img.alpha_composite(lay)
            ca = ease((t - (T_ANS + len(ops) * 0.6 + 0.6)) / 0.4) * out
            if ca > 0:
                lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
                yl = int(yq + sum(70 + 60 * len(x) + 26 for x in op_lines) + 40)
                text_c(ld, (540, yl), 'COMENTA TU RESPUESTA', bebas(66), CG_GOLD + (int(255 * ca),))
                img.alpha_composite(lay)
        # 3) closing card
        if t >= T_END:
            e = ease((t - T_END) / 0.5)
            img.alpha_composite(Image.new('RGBA', (W, H), CG_DARK + (int(200 * e),)))
            gl = Image.new('L', (W, H), 0); ImageDraw.Draw(gl).ellipse((140, 520, 940, 1120), fill=int(110 * e)); gl = gl.filter(ImageFilter.GaussianBlur(110))
            img.alpha_composite(Image.merge('RGBA', (*Image.new('RGB', (W, H), (255, 170, 40)).split(), gl)))
            wordmark(img, 300, e)
            grad_text(img, (540, 700), '¿TÚ QUÉ', bebas(220), e, spacing=6)
            grad_text(img, (540, 900), 'DICES?', bebas(220), e, spacing=6)
            m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).rounded_rectangle((110, 1080, 970, 1230), radius=30, fill=int(255 * e))
            u2 = np.clip((np.arange(W) - 110) / 860, 0, 1)[None, :, None]
            col = np.array(CG_GOLD, np.float32) * (1 - u2) + np.array(CG_ORANGE, np.float32) * u2
            img.alpha_composite(Image.merge('RGBA', (*Image.fromarray(np.repeat(col, H, 0).astype(np.uint8)).split(), m)))
            lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
            text_c(ld, (540, 1158), 'COGNOGYM.COM/DEBATE', bebas(92), (26, 15, 15, int(255 * e)))
            text_c(ld, (540, 1310), 'Vota en un toque', outfit(48, 700), (240, 240, 245, int(255 * e)))
            text_c(ld, (540, 1380), 'Nueva pregunta cada día a las 7:00 a.m.', outfit(36, 600), CG_MUTED + (int(255 * e),))
            img.alpha_composite(lay)
            fo = clamp((t - (DUR - 0.35)) / 0.35)
            if fo > 0: img.alpha_composite(Image.new('RGBA', (W, H), (0, 0, 0, int(255 * fo))))
        return img.convert('RGB')

    if os.environ.get('MUESTRA'):
        for t in map(float, os.environ['MUESTRA'].split(',')): frame(t).save('muestra-%04.1f.jpg' % t, quality=90)
        return
    tmp = tempfile.mkdtemp()
    info = {'duration': DUR, 't_show': 0.0, 't_hide': T_Q, 't_stop': T_SWAP, 't_ask': T_Q, 'roll': False,
            'swap_times': [[T_SWAP - 0.2, T_SWAP + 0.5]] + [[T_ANS + k * 0.6 - 0.15, T_ANS + k * 0.6 + 0.3] for k in range(len(ops))],
            't_brand': T_END}
    json.dump(info, open(os.path.join(tmp, 'info.json'), 'w'))
    subprocess.run([sys.executable, os.path.join(HERE, 'musica.py'), os.path.join(tmp, 'info.json'), os.path.join(tmp, 'm.wav')], check=True, cwd=tmp)
    vid = os.path.join(tmp, 'v.mp4')
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '%dx%d' % (W, H), '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', vid], stdin=subprocess.PIPE)
    for i in range(int(DUR * FPS)): ff.stdin.write(frame(i / FPS).tobytes())
    ff.stdin.close(); assert ff.wait() == 0
    part = salida[:-4] + '.part.mp4'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', vid, '-i', os.path.join(tmp, 'm.wav'), '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-shortest', '-movflags', '+faststart', part], check=True)
    os.replace(part, salida)

if __name__ == '__main__':
    main(*sys.argv[1:4])
