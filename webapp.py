from flask import  Flask, request, send_from_directory
import sqlite3
import json
conn = sqlite3.connect('messages.sqlite')


app = Flask(__name__, static_url_path='')

@app.route('/')
def root():
    return app.send_static_file('index.html')


@app.route("/data/<device_id>")
def data(device_id):
    c = conn.cursor()
    c.execute('select message from messages where deviceid = ? ORDER BY date',[device_id])
    results = c.fetchall()
    return json.dumps(list(map(lambda x: json.loads(x[0].decode()), results)))

if __name__ == "__main__":
    app.run()