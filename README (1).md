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

## Rebuilding

```
sh build.sh
```

Needs Python 3 with Pillow, NumPy and SciPy, and ffmpeg. It rebuilds every video: `sigue.py` and `respuesta.py` (challenge 1), `fortress.py`
(challenge 2), and `musica.py` (the music, made from scratch, nothing licensed). Fonts: Anton and Outfit, both under the SIL Open Font
License (`OFL-*.txt`).
