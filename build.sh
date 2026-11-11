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
rm -f video.mp4 respuesta-video.mp4 musica.wav musica-respuesta.wav info.json info-respuesta.json
echo "Done: every challenge and its answer video"
