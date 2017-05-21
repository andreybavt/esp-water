import paho.mqtt.client as mqtt
import sqlite3
import datetime
import json
conn = sqlite3.connect('messages.sqlite')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS messages (date date, deviceid number, message text)''')



def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("ABA/WATER/+/FROM")

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    message = json.loads(msg.payload.decode())
    c.execute('INSERT INTO messages VALUES (?,?,?)', (datetime.datetime.now(),message['id'], msg.payload))
    conn.commit()

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("broker.mqttdashboard.com", 1883, 60)
client.loop_forever()

