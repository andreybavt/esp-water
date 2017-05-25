#!/usr/bin/env bash
esptool.py --port /dev/ttyUSB0 erase_flash
esptool.py --port /dev/ttyUSB0 --baud 460800 write_flash --flash_size=detect -fm dio 0 /home/andrey/Downloads/esp8266-ota-20170520-v1.8.7-778-g338f0849.bin
echo Sleep 10 ...
sleep 10
echo Reset
ampy --port /dev/ttyUSB0 reset
echo Sleep 10 ...
sleep 10
echo Run initial-setup.py ...
ampy --port /dev/ttyUSB0 run ./initial-setup.py
echo Reset
ampy --port /dev/ttyUSB0 reset
echo Sleep 10 ...
sleep 10
echo Run install-packages.py
ampy --port /dev/ttyUSB0 run ./install-packages.py
echo Write main.py ...
ampy --port /dev/ttyUSB0 put ../main.py /main.py
echo Write wifiConnecter.py ...
ampy --port /dev/ttyUSB0 put ../wifiConnecter.py /wifiConnecter.py
echo Reset
ampy --port /dev/ttyUSB0 reset
sleep 3

echo DONE Initialization!
