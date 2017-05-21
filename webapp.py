from flask import Flask
import sqlite3
import json
conn = sqlite3.connect('messages.sqlite')

app = Flask(__name__)

@app.route("/")
def hello():
    c = conn.cursor()
    c.execute('select message from messages ORDER BY date')
    results = c.fetchmany(100)

    return json.dumps({"result":list(map(lambda x: x[0].decode(),results))})

if __name__ == "__main__":
    app.run()