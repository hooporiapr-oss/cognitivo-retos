#!/bin/sh
# Builds both videos of the "¿Puedes seguir el balón?" challenge.
# Needs: python3 with pillow, numpy, scipy; and ffmpeg.
set -e
cd "$(dirname "$0")"
python3 sigue.py render
python3 musica.py info.json musica.wav
ffmpeg -y -loglevel error -i video.mp4 -i musica.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest sigue-el-balon.mp4
python3 respuesta.py render
python3 musica.py info-respuesta.json musica-respuesta.wav
ffmpeg -y -loglevel error -i respuesta-video.mp4 -i musica-respuesta.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest sigue-el-balon-respuesta.mp4
rm -f video.mp4 respuesta-video.mp4 musica.wav musica-respuesta.wav info.json info-respuesta.json
echo "Done: sigue-el-balon.mp4 and sigue-el-balon-respuesta.mp4"
