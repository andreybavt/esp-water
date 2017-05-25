import utime as time
import network
import json

try:
    import usocket as socket
except:
    import socket

__all__ = [
    'serveConnectToWifiScreen'
]


def breakLine(html, size):
    for i in range(int(len(html) / size) + 1):
        yield html[size * i: size * (i + 1)]


HEADER_OK = """HTTP/1.0 200 OK

"""
HEADER_ERR = """HTTP/1.0 500 Internal Server Error

"""


def serveConnectToWifiScreen(ID='mock-id', micropython_optimize=True):
    s = socket.socket()
    wifiClient = network.WLAN(network.STA_IF)
    wifiAP = network.WLAN(network.AP_IF)
    wifiClient.active(False)
    wifiAP.active(True)

    # Binding to all interfaces - server will be accessible to other hosts!
    ai = socket.getaddrinfo("0.0.0.0", 80)
    print("Bind address info:", ai)
    addr = ai[0][-1]

    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(50)
    print("Listening, connect your browser to http://<this_host>:80/")
    HTML = """<!DOCTYPE html><html lang="en" style="height: 100%"><head> <meta charset="UTF-8"> <style type="text/css"> .success-div{color: green; width: 100%; text-align: center;}.error-div{color: red; width: 100%; text-align: center;}input, select{padding-left: 5px; box-sizing: border-box; height: 30px; width: 100%;}button{height: 30px;}.form-container{width: 400px; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); padding: 20px; background-color: white; box-shadow: rgb(119, 119, 119) 0px 10px 6px -6px;}body{height: 100%; margin: 0; background-color: #ece9e7;}form{background-color: white;}table{width: 400px; table-layout: fixed;}tr{height: 50px;}td{width: 50%;}form tr td:nth-child(2){text-align: right;}form tr td:nth-child(2) > *{width: 100%}</style> <title>Wifindula</title></head><body><div class="form-container"> <form method="post" id="form"> <table> <tr> <td>Device ID</td><td> <div style="overflow: hidden; text-overflow: ellipsis">{{ID}}</div></td></tr><tr> <td><label for="wifi">Wifi name</label></td><td><select name="wifi" id="wifi" required>{{OPTIONS}}</select></td></tr><tr> <td><label for="password">Password</label></td><td> <div><input type="password" name="password" id="password"></div></td></tr><tr> <td colspan="2"> <button style="width: 100%;" type="submit">Connect</button> </td></tr></table> </form></div><script>let form=document.getElementById('form'); let errDiv=document.createElement("div"); errDiv.setAttribute('class', 'error-div'); function doSubmit(e){errDiv.remove(); if (e.preventDefault) e.preventDefault(); data={}; for (let pair of new FormData(form).entries()){data[pair[0]]=pair[1];}fetch("/connect",{method: "POST", body: JSON.stringify(data)}).then(function (response){if (response.ok){return response.text()}else{response.text().then(errReason=>{errDiv.innerHTML='<code>' + errReason + '</code>'; document.getElementById('form').append(errDiv); return null});}}).then(function (data){if (data){form.remove(); let successDiv=document.createElement("div"); successDiv.setAttribute('class', 'success-div'); successDiv.innerHTML='<h4>Device is connected</h4><a href="{{URL}}">See humidity</a>'; document.getElementsByClassName('form-container')[0].append(successDiv); console.log(data);}});}if (form.attachEvent){form.attachEvent("submit", doSubmit);}else{form.addEventListener("submit", doSubmit);}</script></body></html>"""

    counter = 0
    while True:
        res = s.accept()
        client_sock = res[0]
        client_addr = res[1]
        print("Client address:", client_addr)
        print("Client socket:", client_sock)

        if not micropython_optimize:
            client_stream = client_sock.makefile("rwb")
        else:
            client_stream = client_sock

        print("Request")
        req = client_stream.readline()
        print(req)

        method, uri = req.decode().split(' ')[:2]

        print('comparing url' + str((method, uri)))
        if uri == '/':
            print('/root')
            if method == 'GET':
                print('(GET)')
                readStream(client_stream)
                client_stream.write(HEADER_OK)
                rows = ['<option value="%s">%s</option>' % (ap, ap) for ap in scanWifiNetworks(wifiClient)]
                response = HTML.replace('{{OPTIONS}}', ''.join(rows)) \
                    .replace("{{ID}}", ID) \
                    .replace("{{URL}}", ID)
                for chunk in breakLine(response, 1024):
                    client_stream.write(chunk)
        hasInternet = False
        if uri == '/connect' and method == 'POST':
            readStream(client_stream)
            data = client_stream.recv(1024)
            params = json.loads(data.decode())
            if params['wifi']:
                print('Activating Client')
                wifiClient.active(True)
                print('Connecting to AP')
                if not wifiClient.isconnected():
                    wifiClient.disconnect()
                wifiClient.connect(params['wifi'], params['password'])
                for i in range(20):
                    print('Checking connection : ' + str(i))
                    connectionOK = wifiClient.isconnected()
                    if connectionOK:
                        break
                    else:
                        time.sleep(1)
                if connectionOK:
                    hasInternet = isConnectedToInternet()
                    if hasInternet:
                        client_stream.write(HEADER_OK)
                        client_stream.write('OK')
                    else:
                        wifiClient.active(False)
                        client_stream.write(HEADER_ERR)
                        client_stream.write('No internet for AP ' + params['wifi'])
                else:
                    wifiClient.active(False)
                    client_stream.write(HEADER_ERR)
                    client_stream.write('Could not connect to AP ' + params['wifi'])

        client_stream.close()
        if hasInternet:
            time.sleep(1)
            wifiAP.active(False)
        if not micropython_optimize:
            client_sock.close()
        counter += 1
        print()


def scanWifiNetworks(wifiClient):
    wifiClient.active(True)
    accessPoints = wifiClient.scan()
    wifiClient.active(False)
    accessPoints.sort(key=lambda x: x[3], reverse=True)  # 0(reverse = False) - name , 3(reverse = True) - strength
    apSet = set()
    for ap in accessPoints:
        apSet.add(ap[0].decode())
    return apSet


def isConnectedToInternet():
    s = socket.socket()
    try:
        s.connect(('8.8.8.8', 53))
        return True
    except:
        return False
    finally:
        s.close()


def readStream(client_stream):
    while True:
        h = client_stream.readline()
        if h == b"" or h == b"\r\n":
            break
        print(h)