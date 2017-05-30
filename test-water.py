import machine
import utime

pin = machine.Pin(14, machine.Pin.OUT, machine.Pin.PULL_UP)
while True:
    pin.value(0)
    print(0)
    utime.sleep(5)
    pin.value(1)
    print(1)
    utime.sleep(5)
