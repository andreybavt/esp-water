import utime
import machine
import ubinascii
import uhashlib
from uasyncio import sleep, get_event_loop
from umqtt.simple import MQTTClient
import network

# READ Startup button configuration
ledPin = machine.Pin(2, machine.Pin.OUT, machine.Pin.PULL_UP)
pumpPin = machine.Pin(14, machine.Pin.OUT, machine.Pin.PULL_UP)  # wemos = 5
waterLimitPin = machine.Pin(12, machine.Pin.IN, machine.Pin.PULL_UP)  # wemos = 6

needResetWifi = False

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
isWifiPreset = wlan.status() != network.STAT_IDLE
print('isWifiPreset: ' + str(isWifiPreset))
if isWifiPreset:
    for i in range(10):
        needResetWifi = machine.Pin(5, machine.Pin.IN, machine.Pin.PULL_UP).value() == 0
        ledPin.value(0)
        utime.sleep(0.1)
        ledPin.value(1)
        utime.sleep(0.1)

ID = ubinascii.hexlify(uhashlib.sha256(machine.unique_id() + 'SALTY-SALT').digest()).decode()


def normalBoot():
    import json
    import socket
    global client, doWater, adc, STARTUP_TIME, time, TOPIC_FROM, TOPIC_TO, command_processor, on_message

    print('Normal start')

    wlan = network.WLAN(network.STA_IF)
    while wlan.status() == network.STAT_CONNECTING:
        print('WIFI STATUS : {0}'.format(wlan.status()))
        utime.sleep(0.1)
    adc = machine.ADC(0)

    def http_get(url):
        _, _, host, path = url.split('/', 3)
        addr = socket.getaddrinfo(host, 80)[0][-1]
        s = socket.socket()
        s.connect(addr)
        s.send(bytes('GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (path, host), 'utf8'))
        d = ''
        while True:
            data = s.recv(100)
            if data:
                d += str(data, 'utf8')
            else:
                break
        s.close()
        return d[d.find('\r\n\r\n') + 4:len(d)]

    STARTUP_TIME = json.loads(http_get("http://time.jsontest.com/"))['milliseconds_since_epoch'] - utime.ticks_ms()

    def time():
        return utime.ticks_ms() + STARTUP_TIME

    print('Current time : ' + str(time()))
    print(ID)
    TOPIC_BASE = b"ABA/WIFINDULA/{0}/".format(ID)
    TOPIC_FROM = TOPIC_BASE + "FROM"
    TOPIC_TO = TOPIC_BASE + "TO"

    async def doWater(message):
        print('WATERING...' + str(message))
        pumpPin.value(0)
        await sleep(int(message['duration']))
        pumpPin.value(1)
        print('END WATERING!!! ')

    def submitWater(message):
        print("Submit water")
        loop.create_task(doWater(message))
        loop.create_task(pub_every(client, 1, 20))

    class CommandProcessor:
        def __init__(self):
            self.processors = {}

        def register_processor(self, command, processor):
            if command not in self.processors:
                self.processors[command] = []
            self.processors[command].append(processor)

        def get_processors(self, command):
            return self.processors[command]

        def process(self, command, message):
            print('Processing {0} : {1}'.format(command, str(command in self.processors)))

            if command in self.processors:
                for processor in self.processors[command]:
                    processor(message)

    command_processor = CommandProcessor()
    command_processor.register_processor("water", submitWater)

    def on_message(topic, msg):
        message_json = json.loads(msg)
        command_processor.process(message_json['command'], message_json)

    def connect(server="test.mosca.io"):
        c = MQTTClient("aba-water-sensor-" + ID, server, 1883)
        c.set_callback(on_message)
        c.connect()
        c.subscribe(TOPIC_TO)
        return c

    async def poll(client):
        while True:
            client.check_msg()
            await sleep(0)

    async def pub_every(c, interval, iterations=-1):
        if iterations < 0:
            while True:
                doPublish(c)
                await sleep(interval)
        else:
            for i in range(iterations):
                doPublish(c)
                await sleep(interval)

    def doPublish(c):
        message = {'id': ID, 'time': str(time()), 'moisture': adc.read()}
        print('publish ' + str(message))
        c.publish(TOPIC_FROM, json.dumps(message))

    loop = get_event_loop()
    client = connect()
    loop.create_task(poll(client))
    loop.create_task(pub_every(client, 10))
    loop.run_forever()


if needResetWifi or not isWifiPreset:
    from wifiConnecter import serveConnectToWifiScreen

    serveConnectToWifiScreen(ID)
    print('WIFI configured, starting a normal boot...')
    normalBoot()
else:
    normalBoot()
