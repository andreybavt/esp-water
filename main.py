from umqtt.simple import MQTTClient
from uasyncio import sleep, get_event_loop
from utime import time
import gc
import uhashlib
from machine import unique_id
import ubinascii
import json

ID = ubinascii.hexlify(uhashlib.sha256(unique_id() + 'SALTY-SALT').digest()).decode()
print(ID)
TOPIC_BASE = b"ABA/WATER/{0}/".format(ID)
TOPIC_FROM = TOPIC_BASE + "FROM"
TOPIC_TO = TOPIC_BASE + "TO"

def sleep_my(endSleepTime):
    while True:
        curr = time()
        if curr > endSleepTime:
            break
        yield

# print("Start waiting")
# for i in sleep_my(time() + 5):
#     pass
# print("End waiting")


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


command_processor = CommandProcessor()

command_processor.register_processor("measure", lambda x: print("Measuring ..."))
command_processor.register_processor("water", lambda x: print("Watering ..."))


def on_message(topic, msg):
    message_json = json.loads(msg)
    command_processor.process(message_json['command'], message_json)


def connect(server="iot.eclipse.org"):
    c = MQTTClient("aba-water-client-"+ID, server,1883)
    c.set_callback(on_message)
    c.connect()
    c.subscribe(TOPIC_TO)
    return c


async def poll(client):
    while True:
        client.check_msg()
        await sleep(0)


async def pub_every(c, message, interval):
    while True:
        c.publish(TOPIC_FROM, json.dumps({'id': ID, 'time': str(time()), 'memory': str(gc.mem_free())}))
        await sleep(interval)


loop = get_event_loop()
client = connect()
loop.create_task(poll(client))
loop.create_task(pub_every(client, "Hello from ESP12e!, hardware speaking", 5))
loop.run_forever()
