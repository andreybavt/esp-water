import network
from utime import time
print("Starting initial setup")
print("Enabling network")
network.WLAN(network.AP_IF).active(False)
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
print("Connecting to AP")
sta_if.connect('AndroidAPaba', 'logarithm')

def sleep_my(startTime):
    while True:
        curr = time()
        if curr > startTime:
            break
        yield

SLEEP = 5
print("Going to sleep for "+str(SLEEP)+" seconds...")
for i in sleep_my(time() + SLEEP):
    pass
print("Woke up")
