import json
import mysql.connector
import os
import paho.mqtt.publish as publish
import pandas as pd
from datetime import datetime, timedelta
from flask import Flask, request
from scipy import signal

conn = mysql.connector.connect(user='water', password=os.environ['WATER_DB_PASS'],
                               host='51.75.64.137',
                               database='water',
                               auth_plugin='mysql_native_password')
app = Flask(__name__, static_url_path='')


@app.route('/')
def root():
    return app.send_static_file('index.html')


@app.route("/data/<device_id>")
def data(device_id):
    c = conn.cursor()
    c.execute('SELECT * FROM (SELECT message FROM messages WHERE deviceid = %s ORDER BY date DESC) tt LIMIT 1000',
              [device_id])
    # c.execute('select message from (select date,deviceid, message from (SELECT      @i:=@i+1 AS iterator,      t.* FROM      messages AS t,     (SELECT @i:=0) AS foo) tt where tt.iterator % 50 = 0 and tt.deviceid = %s order by date desc LIMIT 3000) asd', [device_id])
    results = c.fetchall()
    # return json.dumps(list(map(lambda x: json.loads(x[0].decode()), results)))

    result = [json.loads(r[0]) for r in results]
    frame = pd.DataFrame(result, columns=['moisture', 'id', 'time', 'outOfWater'])
    frame.sort_values('time', inplace=True)
    print('DATA FRAME SHAPE : ' + str(frame.shape))
    frame['moisture'] = signal.savgol_filter(frame['moisture'],
                                             (frame.shape[0] if frame.shape[0] % 2 else frame.shape[0] - 1) if
                                             frame.shape[0] < 51 else 51,
                                             3).tolist()
    return frame.to_json(orient='records')


@app.route("/water/<duration>", methods=["POST"])
def water(duration):
    print('HOHOHOHOHOHO')
    data = json.loads(request.data.decode())
    # avgMoisture = float(c.fetchone())
    c = conn.cursor()
    device_id = data['id']
    c.execute("SELECT date FROM waterActions WHERE deviceid = %s AND date > DATE_SUB(NOW(), INTERVAL 8 HOUR);",
              [device_id])
    results = c.fetchall()

    lastWaterDates = [r[0] for r in results]
    lastWaterDates.sort()
    if len(lastWaterDates) < 2 or ('admin' in data and data['admin'] == '1'):
        c.execute("INSERT INTO waterActions(date, deviceid) VALUES (%s,%s)", [datetime.now(), device_id])
        conn.commit()

        publish.single("ABA/WIFINDULA/{0}/TO".format(device_id),
                       json.dumps({'id': device_id, 'command': 'water', 'duration': duration}),
                       hostname="broker.hivemq.com")
        return json.dumps({'status': 'ok', 'text': 'Watered successfully!'})

    return json.dumps({'status': 'error',
                       'text': 'Too many water requests, next watering is available on {0} UTC'.format(
                           lastWaterDates[len(lastWaterDates) - 1] + timedelta(hours=2))})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8989)
