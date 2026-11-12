#!/bin/sh
# Builds every challenge video and its answer video.
# Needs: python3 with pillow, numpy, scipy; and ffmpeg.
set -e
cd "$(dirname "$0")"
python3 sigue.py render
python3 musica.py info.json musica.wav
ffmpeg -y -loglevel error -i video.mp4 -i musica.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest sigue-el-balon.mp4
python3 respuesta.py render
python3 musica.py info-respuesta.json musica-respuesta.wav
ffmpeg -y -loglevel error -i respuesta-video.mp4 -i musica-respuesta.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest sigue-el-balon-respuesta.mp4
# challenge 2: ¿Quién tiene el balón?
python3 quien.py reto render
python3 musica.py info-quien-tiene-el-balon.json quien.wav
ffmpeg -y -loglevel error -i quien-video.mp4 -i quien.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest quien-tiene-el-balon.mp4
python3 quien.py respuesta render
python3 musica.py info-quien-tiene-el-balon-respuesta.json quien-respuesta.wav
ffmpeg -y -loglevel error -i quien-respuesta-video.mp4 -i quien-respuesta.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest quien-tiene-el-balon-respuesta.mp4
rm -f quien-video.mp4 quien-respuesta-video.mp4 quien.wav quien-respuesta.wav info-quien-*.json
# challenge 3: ¿Quién tiene el balón? Nivel 2
python3 nivel2.py reto render
python3 musica.py info-quien-nivel-2.json nivel2.wav
ffmpeg -y -loglevel error -i nivel2-video.mp4 -i nivel2.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest quien-tiene-el-balon-nivel-2.mp4
python3 nivel2.py respuesta render
python3 musica.py info-quien-nivel-2-respuesta.json nivel2-respuesta.wav
ffmpeg -y -loglevel error -i nivel2-respuesta-video.mp4 -i nivel2-respuesta.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest quien-tiene-el-balon-nivel-2-respuesta.mp4
rm -f nivel2-video.mp4 nivel2-respuesta-video.mp4 nivel2.wav nivel2-respuesta.wav info-quien-nivel-2*.json
# challenge: ¿Quién tiene el balón? 5 balones
python3 cinco.py reto render
python3 musica.py info-cinco.json cinco.wav
ffmpeg -y -loglevel error -i cinco-video.mp4 -i cinco.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest cinco-balones.mp4
python3 cinco.py respuesta render
python3 musica.py info-cinco-respuesta.json cinco-respuesta.wav
ffmpeg -y -loglevel error -i cinco-respuesta-video.mp4 -i cinco-respuesta.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest cinco-balones-respuesta.mp4
rm -f cinco-video.mp4 cinco-respuesta-video.mp4 cinco.wav cinco-respuesta.wav info-cinco*.json
rm -f video.mp4 respuesta-video.mp4 musica.wav musica-respuesta.wav info.json info-respuesta.json
echo "Done: every challenge and its answer video"
