# Cognitivo Retos

Weekly attention and memory challenges for Cognitivo Gym: short portrait
videos (1080×1920) made to be shared, each with an answer video for the
next day. Every video ends on the Cognitivo Gym card.

Every challenge follows the model of challenge 1: a quick game of watching
and following on the court, not a copy of the Cognitivo Gym training games.

## Challenge 1 · ¿Puedes seguir el balón?

| File | What it is |
|---|---|
| `sigue-el-balon.mp4` | The challenge (21 s). Three basketballs on a neon player; follow the one marked in red through 18 swaps, then comment 1, 2 or 3. |
| `sigue-el-balon-respuesta.mp4` | The answer (26 s). The same swaps in slow motion with the ball kept red, ending on "¡ERA EL 2!". Post it the next day. |

**The answer is 2** (the left hand). The moves are fixed, so it is the same every time the videos are built.

## Rebuilding

```
sh build.sh
```

Needs Python 3 with Pillow, NumPy and SciPy, and ffmpeg. It rebuilds both videos: `sigue.py` and `respuesta.py` (the challenge and its answer), and `musica.py` (the music, made from scratch, nothing licensed). Fonts: Anton and Outfit, both under the SIL Open Font
License (`OFL-*.txt`).
