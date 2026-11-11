# Cognitivo Retos

Weekly attention and memory challenges for Cognitivo Gym: short portrait
videos (1080×1920) made to be shared, each with an answer video for the
next day. Every video ends on the Cognitivo Gym card.

## Challenge 1 · ¿Puedes seguir el balón?

| File | What it is |
|---|---|
| `sigue-el-balon.mp4` | The challenge (21 s). Three basketballs on a neon player; follow the one marked in red through 18 swaps, then comment 1, 2 or 3. |
| `sigue-el-balon-respuesta.mp4` | The answer (26 s). The same swaps in slow motion with the ball kept red, ending on "¡ERA EL 2!". Post it the next day. |

**The answer is 2** (the left hand). The moves are fixed, so it is the same every time the videos are built.

## Challenge 2 · ¿Puedes recordar el orden? (The Fortress)

| File | What it is |
|---|---|
| `fortress-orden.mp4` | The challenge (14 s). The real Fortress board: five targets in a 2-1-2 on a court. Six light up one at a time, each with its own note; then: which colour lit up 4th? Comment the colour. |
| `fortress-orden-respuesta.mp4` | The answer (15 s). The chain plays back slowly, leaving a number on each target, ending on "¡ERA EL ROSA!" with the whole order. |

**The answer is ROSA** (pink). The order is dorado, naranja, morado, rosa, cian, naranja.

## Challenge 3 · ¿Puedes recordar los números? (The Recall)

| File | What it is |
|---|---|
| `recall-donde-3.mp4` | The challenge (15 s). Numbers 1 to 5 appear on the court one at a time, then vanish. Four squares get a letter: where was the 3? Comment A, B, C or D. |
| `recall-donde-3-respuesta.mp4` | The answer (14 s). The numbers come back one by one, ending on "¡ERA LA C!". |

**The answer is C.**

## Challenge 4 · ¿Ves el cambio? (The Recognition)

| File | What it is |
|---|---|
| `recognition-cambio.mp4` | The challenge (15 s). A gold pattern of six squares, then its echo in lime with one square moved. Which one moved? Comment the letter (A to F). |
| `recognition-cambio-respuesta.mp4` | The answer (14 s). The echo with the original dotted in, ending on "¡ERA LA E!". |

**The answer is E** (it moved one square to the right).

## Rebuilding

```
sh build.sh
```

Needs Python 3 with Pillow, NumPy and SciPy, and ffmpeg. It rebuilds every video: `sigue.py` and `respuesta.py` (challenge 1), `fortress.py`
(challenge 2), `recall_recog.py` (challenges 3 and 4), and `musica.py` (the music, made from scratch, nothing licensed). Fonts: Anton and Outfit, both under the SIL Open Font
License (`OFL-*.txt`).
