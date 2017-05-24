import utime
import machine

# READ Startup button configuration
ledPin = machine.Pin(2, machine.Pin.OUT, machine.Pin.PULL_UP)
needResetWifi = False
for i in range(10):
    needResetWifi = machine.Pin(5, machine.Pin.IN, machine.Pin.PULL_UP).value() == 0
    ledPin.value(0)
    utime.sleep(0.1)
    ledPin.value(1)
    utime.sleep(0.1)


if needResetWifi:
    # import network
    # ap_if = network.WLAN(network.AP_IF)
    # sta_if = network.WLAN(network.STA_IF)
    # sta_if.active(False)
    # ap_if.active(True)
    # import machine
    #
    # html = """<!DOCTYPE html><html lang="en" style="height: 100%"><head> <meta charset="UTF-8"> <style type="text/css"> button{height: 30px;}.form-container{position: absolute; padding: 20px; background-color: white; box-shadow: rgb(119, 119, 119) 0px 10px 6px -6px; top: 50%; left: 50%; transform: translate(-50%, -50%);}body{height: 100%; margin: 0; background-color: #ece9e7;}form{background-color: white;}table{width: 400px;}tr{height: 50px;}td{width: 50%;}form tr td:nth-child(2){text-align: right;}form tr td:nth-child(2) > *{width: 100%}</style> <title>Wifindula</title></head><body><script>function doSubmit(){alert(1) console.log('submit') let kvpairs=[]; let form=document.getElementById('connectionForm'); for (let i=0; i < form.elements.length; i++){let e=form.elements[i]; kvpairs.push(encodeURIComponent(e.name) + "=" + encodeURIComponent(e.value));}let queryString=kvpairs.join("&");}</script><div class="form-container"> <form method="post" id="connectionForm"> <table> <tr> <td><label for="wifi">Wifi name</label></td><td><select name="wifi" id="wifi" required> {{options}} </select></td></tr><tr> <td><label for="password">Password</label></td><td><input type="password" name="password" id="password"></td></tr><tr> <td colspan="2"> <button style="width: 100%;" type="submit">Connect</button> </td></tr></table> </form></div></body></html>"""
    # import socket
    #
    # addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    #
    # s = socket.socket()
    # s.bind(addr)
    # s.listen(5)
    #
    # print('listening on', addr)
    #
    # while True:
    #     cl, addr = s.accept()
    #
    #     sta_if.active(True)
    #     accessPoints = sta_if.scan()
    #     sta_if.active(False)
    #     accessPoints.sort(key=lambda x: x[3], reverse=True) #0(reverse = False) - name , 3(reverse = True) - strength
    #     apSet = set()
    #     for ap in accessPoints:
    #         apSet.add(ap[0].decode())
    #
    #
    #     print('client connected from', addr)
    #     cl_file = cl.makefile('rwb', 0)
    #     while True:
    #         line = cl_file.readline()
    #         if not line or line == b'\r\n':
    #             break
    #     rows = ['<option value="%s">%s</option>' % (ap, ap) for ap in apSet]
    #     response = html.replace('{{options}}', '\n'.join(rows))
    #     chunks, chunk_size = len(response), int(len(response) / 100)
    #     for ch in [ response[i:i+chunk_size] for i in range(0, chunks, chunk_size) ]:
    #         cl.send(ch)
    #     cl.close()
    try:
        import usocket as socket
    except:
        import socket

    CONTENT = b"""\
    HTTP/1.1 200 OK
    Content-Type: text/html

    Hello #%d from MicroPython!
    """


    def main(micropython_optimize=False):
        s = socket.socket()

        # Binding to all interfaces - server will be accessible to other hosts!
        ai = socket.getaddrinfo("0.0.0.0", 8080)
        print("Bind address info:", ai)
        addr = ai[0][-1]

        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(addr)
        s.listen(5)
        print("Listening, connect your browser to http://<this_host>:8080/")

        counter = 0
        while True:
            res = s.accept()
            client_sock = res[0]
            client_addr = res[1]
            print("Client address:", client_addr)
            print("Client socket:", client_sock)

            if not micropython_optimize:
                # To read line-oriented protocol (like HTTP) from a socket (and
                # avoid short read problem), it must be wrapped in a stream (aka
                # file-like) object. That's how you do it in CPython:
                client_stream = client_sock.makefile("rwb")
            else:
                # .. but MicroPython socket objects support stream interface
                # directly, so calling .makefile() method is not required. If
                # you develop application which will run only on MicroPython,
                # especially on a resource-constrained embedded device, you
                # may take this shortcut to save resources.
                client_stream = client_sock

            print("Request:")
            req = client_stream.readline()
            print(req)
            while True:
                h = client_stream.readline()
                if h == b"" or h == b"\r\n":
                    break
                print(h)
            client_stream.write(CONTENT % counter)

            client_stream.close()
            if not micropython_optimize:
                client_sock.close()
            counter += 1
            print()


    main()



else :
    from umqtt.simple import MQTTClient
    from uasyncio import sleep, get_event_loop
    import gc
    import uhashlib
    import ubinascii
    import json
    import socket
    print('Normal start')



#
#
# adc = machine.ADC(0)
#
#
# def http_get(url):
#     _, _, host, path = url.split('/', 3)
#     addr = socket.getaddrinfo(host, 80)[0][-1]
#     s = socket.socket()
#     s.connect(addr)
#     s.send(bytes('GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (path, host), 'utf8'))
#     d = ''
#     while True:
#         data = s.recv(100)
#         if data:
#             d += str(data, 'utf8')
#         else:
#             break
#     s.close()
#     return d[d.find('\r\n\r\n') + 4:len(d)]
#
#
# STARTUP_TIME = json.loads(http_get("http://time.jsontest.com/"))['milliseconds_since_epoch'] - utime.ticks_ms()
#
#
# def time():
#     return utime.ticks_ms() + STARTUP_TIME
#
#
# print('Current time : ' + str(time()))
#
# ID = ubinascii.hexlify(uhashlib.sha256(machine.unique_id() + 'SALTY-SALT').digest()).decode()
# print(ID)
# TOPIC_BASE = b"ABA/WATER/{0}/".format(ID)
# TOPIC_FROM = TOPIC_BASE + "FROM"
# TOPIC_TO = TOPIC_BASE + "TO"
#
#
# def sleep_my(endSleepTime):
#     while True:
#         curr = time()
#         if curr > endSleepTime:
#             break
#         yield
#
#
# # print("Start waiting")
# # for i in sleep_my(time() + 5):
# #     pass
# # print("End waiting")
#
#
# class CommandProcessor:
#     def __init__(self):
#         self.processors = {}
#
#     def register_processor(self, command, processor):
#         if command not in self.processors:
#             self.processors[command] = set()
#         self.processors[command].add(processor)
#
#     def get_processors(self, command):
#         return self.processors[command]
#
#     def process(self, command, message):
#         if command in self.processors:
#             for processor in self.processors[command]:
#                 processor(message)
#
#
# command_processor = CommandProcessor()
#
# command_processor.register_processor("measure", lambda x: print("Measuring ..."))
# command_processor.register_processor("water", lambda x: print("Watering ..."))
#
#
# def on_message(topic, msg):
#     message_json = json.loads(msg)
#     command_processor.process(message_json['command'], message_json)
#
#
# def connect(server="broker.mqttdashboard.com"):
#     c = MQTTClient("aba-water-sensor-" + ID, server, 1883)
#     c.set_callback(on_message)
#     c.connect()
#     c.subscribe(TOPIC_TO)
#     return c
#
#
# async def poll(client):
#     while True:
#         client.check_msg()
#         await sleep(0)
#
#
# async def pub_every(c, interval):
#     while True:
#         message = {'id': ID, 'time': str(time()), 'memory': str(gc.mem_free()), 'moisture': adc.read()}
#         print('publish ' + str(message))
#         c.publish(TOPIC_FROM, json.dumps(message))
#         await sleep(interval)
#
#
# loop = get_event_loop()
# client = connect()
# loop.create_task(poll(client))
# loop.create_task(pub_every(client, 7))
# loop.run_forever()
