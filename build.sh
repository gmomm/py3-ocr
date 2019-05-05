#!/usr/bin/env bash
# bash strict mode : http://redsymbol.net/articles/unofficial-bash-strict-mode/
set -euo pipefail
IFS=$'\n\t'

LEPTONICA="leptonica-1.78.0.tar.gz"
TESSERACT="tesseract-master.tar.gz"
TESSERACT_MODEL1="eng.traineddata"
TESSERACT_MODEL2="por.traineddata"
OPENCV_CORE="opencv-4.1.0.tar.gz"
OPENCV_CONTRIB="opencv-contrib-4.1.0.tar.gz"


if [ ! -f ././${LEPTONICA} ]; then
    echo "leptonica not found, downloading tarball"
    curl -L -o ././${LEPTONICA} http://www.leptonica.org/source/leptonica-1.78.0.tar.gz 
fi

if [ ! -f ././${TESSERACT} ]; then
    echo "tesseract not found, downloading tarball"
    curl -L -o ././${TESSERACT} https://github.com/tesseract-ocr/tesseract/archive/master.tar.gz
fi 

if [ ! -f ././${TESSERACT_MODEL1} ]; then
    echo "tessseract model not found, downloading"
    curl -L -o ././${TESSERACT_MODEL} https://github.com/tesseract-ocr/tessdata/raw/master/por.traineddata
fi

if [ ! -f ././${TESSERACT_MODEL2} ]; then
    echo "tessseract model not found, downloading"
    curl -L -o ././${TESSERACT_MODEL} https://github.com/tesseract-ocr/tessdata/raw/master/eng.traineddata
fi

if [ ! -f ././${OPENCV_CORE} ]; then
    echo "opencv core not found, downloading tarball"
    curl -L -o ././${OPENCV_CORE} https://github.com/opencv/opencv/archive/4.1.0.tar.gz
fi

if [ ! -f ././${OPENCV_CONTRIB} ]; then
    echo "opencv contrib not found"
    curl -L -o ././${OPENCV_CONTRIB} https://github.com/opencv/opencv_contrib/archive/4.1.0.tar.gz
fi

echo "building docker container"
docker build --squash -t "gregoriomomm/py3-ocr"  .
