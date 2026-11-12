# Cognitivo Retos

Weekly attention and memory challenges for Cognitivo Gym: short portrait
videos (1080×1920) made to be shared, each with an answer video for the
next day. Every video ends on the Cognitivo Gym card.

Every challenge follows the model of challenge 1: a quick game of watching
and following on the court, not a copy of the Cognitivo Gym training games.

## Challenge 1 · ¿Puedes seguir el balón?

| File | What it is |
|---|---|
| `sigue-el-balon.mp4` | The challenge (21 s). Three basketballs on the Cognitivo Gym court, in the gym's own gold and orange; follow the one marked in red through 18 swaps, then comment 1, 2 or 3. |
| `sigue-el-balon-respuesta.mp4` | The answer (26 s). The same swaps in slow motion with the ball kept red, ending on "¡ERA EL 2!". Post it the next day. |

**The answer is 2** (the left hand). The moves are fixed, so it is the same every time the videos are built.

## Challenge 2 · ¿Quién tiene el balón? 5 balones

| File | What it is |
|---|---|
| `cinco-balones.mp4` | The challenge (19 s). The ball to follow starts with #7; on every one of its passes an identical ball flies in from the sideline, until all five players hold one ("1 BALÓN" … "5 BALONES"). Then "¡A MEZCLAR!": players swap balls in pairs, two swaps at a time, 12 rounds, faster and faster. Lights out: who has the ball that started with #7? |
| `cinco-balones-respuesta.mp4` | The answer (22 s). Slow motion, every ball shown as it comes in, the ball to follow kept red with a red ring and a trail the whole way, ending on "¡ERA EL 14!". |

**The answer is 14.** Made by `cinco.py`. Released before the two-ball and three-ball versions below.

## Challenge 2b · ¿Quién tiene el balón?

| File | What it is |
|---|---|
| `quien-tiene-el-balon.mp4` | The challenge (19 s). Five players (7, 3, 11, 14, 21) on the same court. The ball to follow starts with #7 and is passed alone four times; then an identical second ball comes in from the sideline and both are passed at once, faster and faster. The lights go out on the last catch: who has the ball that started with #7? Comment the number. |
| `quien-tiene-el-balon-respuesta.mp4` | The answer (22 s). The passes in slow motion, the ball to follow in red with a trail and a pass count, the other ball faded, ending on "¡ERA EL 21!". |

**The answer is 21.** Made by `quien.py`.

## Challenge 3 · ¿Quién tiene el balón? Nivel 2

| File | What it is |
|---|---|
| `quien-tiene-el-balon-nivel-2.mp4` | The challenge (25 s). The same game with three identical balls: the one to follow starts with #7, a second ball comes in, then a third. Each beat moves one or two balls, never three, so nobody ever holds two. Lights out on the last catch. |
| `quien-tiene-el-balon-nivel-2-respuesta.mp4` | The answer. Slow motion, the ball to follow in red, the other two faded, ending on "¡ERA EL 11!". |

**The answer is 11.** Made by `nivel2.py`.

## Rebuilding

```
sh build.sh
```

Needs Python 3 with Pillow, NumPy and SciPy, and ffmpeg. It rebuilds every video: `sigue.py` and `respuesta.py` (challenge 1), `cinco.py` (5 balones), `quien.py` (challenge 2), `nivel2.py` (challenge 3), and `musica.py` (the music, made from scratch, nothing licensed). Fonts: Bebas Neue (the gym's wordmark font), Anton and Outfit, all under the SIL Open Font
License (`OFL-*.txt`).
