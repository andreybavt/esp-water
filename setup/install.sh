#!/usr/bin/env bash
cd /home/andrey/git/python/micropython/esp8266
make
cd /home/andrey/git/python/micro/nodemcu/setup
esptool.py --port /dev/ttyUSB0 erase_flash
esptool.py --port /dev/ttyUSB0 --baud 460800 write_flash --flash_size=detect -fm dio 0 /home/andrey/git/python/micropython/esp8266/build/firmware-combined.bin
echo Sleep 10 ...
sleep 10
echo Reset
ampy --port /dev/ttyUSB0 reset
echo Sleep 10 ...
sleep 10
echo Write main.py ...
ampy --port /dev/ttyUSB0 put ../main.py /main.py
echo Write wifi.html ...
ampy --port /dev/ttyUSB0 put ../wifi.html /wifi.html
echo Reset
ampy --port /dev/ttyUSB0 reset
sleep 3

echo DONE Initialization!
