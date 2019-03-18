import datetime
import json
import mysql.connector
import paho.mqtt.client as mqtt
import re
import os


conn = mysql.connector.connect(user='water', password=os.environ['WATER_DB_PASS'],
                               host='51.75.64.137',
                               database='water')

c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS messages (date timestamp, deviceid TEXT, message TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS moisture (date timestamp, deviceid TEXT, moisture real)''')
c.execute('''CREATE TABLE IF NOT EXISTS waterActions (date timestamp, deviceid TEXT)''')
FROM_MESSAGE_REGEX = re.compile('ABA\/WIFINDULA\/[a-zA-Z0-9_]*\/FROM')


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("ABA/WIFINDULA/+/FROM")


def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))
    message = json.loads(msg.payload.decode())
    date = datetime.datetime.fromtimestamp(float(message['time']) / 1000)
    c.execute('INSERT INTO messages VALUES (%s,%s,%s)', (date, message['id'], msg.payload))
    if FROM_MESSAGE_REGEX.match(msg.topic):
        c.execute('INSERT INTO moisture VALUES (%s,%s,%s)', (date, message['id'], message['moisture']))
    conn.commit()


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("broker.hivemq.com", 1883, 60)
client.loop_forever()
