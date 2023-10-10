docker build . -t finance_calc_qt
docker run --rm -it -v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY=$DISPLAY -u qtuser finance_calc_qt python3 /app/main.py
