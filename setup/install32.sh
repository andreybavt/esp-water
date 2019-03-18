#!/usr/bin/env bash
MICROPYTHON_ESP32_PATH=/home/andrey/git/python/micropython-esp32/ports/esp32

for i in uasyncio umqtt wifiConnecter.py wifiMeasurer.py
do
    rm ${MICROPYTHON_ESP32_PATH}/modules/${i}
done

ln -s /home/andrey/.micropython/lib/uasyncio ${MICROPYTHON_ESP32_PATH}/modules/uasyncio
ln -s /home/andrey/.micropython/lib/umqtt ${MICROPYTHON_ESP32_PATH}/modules/umqtt
ln -s /home/andrey/git/python/micro/nodemcu/wifiConnecter.py ${MICROPYTHON_ESP32_PATH}/modules/wifiConnecter.py
ln -s /home/andrey/git/python/micro/nodemcu/wifiMeasurer.py ${MICROPYTHON_ESP32_PATH}/modules/wifiMeasurer.py

cd ${MICROPYTHON_ESP32_PATH}
make
cd /home/andrey/git/python/micro/nodemcu/setup
esptool.py --port /dev/ttyUSB0 erase_flash
esptool.py --port /dev/ttyUSB0 --baud 460800 write_flash --flash_size=detect -fm dio 0 ${MICROPYTHON_ESP32_PATH}/build/firmware-combined.bin
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
