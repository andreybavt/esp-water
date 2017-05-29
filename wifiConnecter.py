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


def read_in_chunks(file_object, chunk_size=1024):
    """Lazy function (generator) to read a file piece by piece.
    Default chunk size: 1k."""
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data


def serveConnectToWifiScreen(ID='mock-id', micropython_optimize=True):
    s = socket.socket()
    wifiClient = network.WLAN(network.STA_IF)
    wifiAP = network.WLAN(network.AP_IF)
    wifiClient.active(False)
    wifiAP.active(True)

    ai = socket.getaddrinfo("0.0.0.0", 80)
    print("Bind address info:", ai)
    addr = ai[0][-1]

    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(50)
    print("Listening, connect your browser to http://<this_host>:80/")

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
                options = ['<option value="%s">%s</option>' % (ap, ap) for ap in scanWifiNetworks(wifiClient)]

                with open('wifi.html', 'r') as f:
                    for piece in read_in_chunks(f, 20):
                        client_stream.write(piece)

                params = {'ID': ID, 'URL': 'http://217.182.206.137/?id=' + ID, 'OPTIONS': ''.join(options)}

                fieldReplacementScript = "<script>String.prototype.replaceAll=function (search, replacement){return this.replace(new RegExp(search, 'g'), replacement);}; let bodyHtml=document.body.innerHTML; let incomingData={{DATA}}; Object.entries(incomingData).forEach(e=> bodyHtml=bodyHtml.replaceAll('{{' + e[0] + '}}', e[1])); document.body.innerHTML=bodyHtml;runInit();</script>"
                fieldReplacementScript = fieldReplacementScript.replace('{{DATA}}', json.dumps(params))

                for chunk in breakLine(fieldReplacementScript, 100):
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

                while wifiClient.status() == network.STAT_CONNECTING:
                    print('Trying to connect, status = ' + str(wifiClient.status()))
                    time.sleep(0.2)

                connectionOK = wifiClient.isconnected()
                print('connectionOK ' + str(connectionOK))
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
            return
        if not micropython_optimize:
            client_sock.close()


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
