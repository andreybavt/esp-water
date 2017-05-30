from flask import Flask, request, send_from_directory
import sqlite3
import json
from datetime import datetime, timedelta
import paho.mqtt.publish as publish

conn = sqlite3.connect('messages.sqlite')

app = Flask(__name__, static_url_path='')


@app.route('/')
def root():
    return app.send_static_file('index.html')


@app.route("/data/<device_id>")
def data(device_id):
    c = conn.cursor()
    c.execute('SELECT message FROM messages WHERE deviceid = ? ORDER BY date', [device_id])
    results = c.fetchall()
    return json.dumps(list(map(lambda x: json.loads(x[0].decode()), results)))


@app.route("/water", methods=["POST"])
def water():
    data = json.loads(request.data.decode())
    # avgMoisture = float(c.fetchone())
    c = conn.cursor()
    device_id = data['id']
    c.execute("SELECT date FROM waterActions WHERE deviceid = ? AND date > datetime('now', '-2 hour');", [device_id])
    results = c.fetchall()

    lastWaterDates = list(map(lambda x: datetime.strptime(x[0], '%Y-%m-%d %H:%M:%S.%f'), results))
    lastWaterDates.sort()
    if len(lastWaterDates) < 2 or ('adminKey' in data and data['adminKey'] == 'yesAdmin'):
        c.execute("INSERT INTO waterActions(date, deviceid) VALUES (?,?)", [datetime.now(), device_id])
        conn.commit()
        publish.single("ABA/WIFINDULA/{0}/TO".format(device_id),
                       json.dumps({'id': device_id, 'command': 'water', 'duration': 20}),
                       hostname="test.mosca.io")
        return json.dumps({'status': 'ok', 'text': 'Watered successfully!'})

    return json.dumps({'status': 'error',
                       'text': 'Too many water requests, next watering is awailable on {0} UTC'.format(
                           lastWaterDates[len(lastWaterDates) - 1] + timedelta(hours=2))})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
