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
python3 fortress.py reto render
python3 musica.py info-fortress-orden.json fortress.wav
ffmpeg -y -loglevel error -i fortress-orden-video.mp4 -i fortress.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest fortress-orden.mp4
python3 fortress.py respuesta render
python3 musica.py info-fortress-orden-respuesta.json fortress-respuesta.wav
ffmpeg -y -loglevel error -i fortress-orden-respuesta-video.mp4 -i fortress-respuesta.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest fortress-orden-respuesta.mp4
rm -f fortress-orden-video.mp4 fortress-orden-respuesta-video.mp4 fortress.wav fortress-respuesta.wav info-fortress-*.json
rm -f video.mp4 respuesta-video.mp4 musica.wav musica-respuesta.wav info.json info-respuesta.json
echo "Done: sigue-el-balon, fortress-orden, and their answer videos"
