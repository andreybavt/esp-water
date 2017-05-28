from uasyncio import sleep, get_event_loop
from umqtt.simple import MQTTClient
import machine
import utime
import json
import socket


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


def time():
    return utime.ticks_ms() + STARTUP_TIME


def sleep_my(endSleepTime):
    while True:
        curr = time()
        if curr > endSleepTime:
            break
        yield


class CommandProcessor:
    def __init__(self):
        self.processors = {}

    def register_processor(self, command, processor):
        if command not in self.processors:
            self.processors[command] = set()
        self.processors[command].add(processor)

    def get_processors(self, command):
        return self.processors[command]

    def process(self, command, message):
        if command in self.processors:
            for processor in self.processors[command]:
                processor(message)


adc = machine.ADC(0)


def main_run(ID):
    global STARTUP_TIME, TOPIC_FROM, TOPIC_TO, command_processor, on_message

    STARTUP_TIME = json.loads(http_get("http://time.jsontest.com/"))['milliseconds_since_epoch'] - utime.ticks_ms()

    print('Normal start')

    print('Current time : ' + str(time()))
    print(ID)
    TOPIC_BASE = b"ABA/WIFINDULA/{0}/".format(ID)
    TOPIC_FROM = TOPIC_BASE + "FROM"
    TOPIC_TO = TOPIC_BASE + "TO"

    command_processor = CommandProcessor()
    command_processor.register_processor("measure", lambda x: print("Measuring ..."))
    command_processor.register_processor("water", lambda x: print("Watering ..."))

    def on_message(topic, msg):
        message_json = json.loads(msg)
        command_processor.process(message_json['command'], message_json)

    def connect(server="broker.mqttdashboard.com"):
        print("connecting to {0}, clientid : {1}".format(server, "aba-water-sensor-" + ID))
        c = MQTTClient("aba-water-sensor-" + ID, server, 1883)
        c.set_callback(on_message)
        c.connect()
        c.subscribe(TOPIC_TO)
        return c

    async def poll(client):
        while True:
            client.check_msg()
            await sleep(0)

    async def pub_every(c, interval):
        while True:
            message = {'id': ID, 'time': str(time()), 'moisture': 1024 - adc.read()}
            print('publish ' + str(message))
            c.publish(TOPIC_FROM, json.dumps(message))
            await sleep(interval)

    loop = get_event_loop()
    client = connect()
    loop.create_task(poll(client))
    loop.create_task(pub_every(client, 7))
    loop.run_forever()
