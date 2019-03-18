server = "broker.hivemq.com"
c = MQTTClient("aba-water-sensor-" + ID, server, 1883)
c.set_callback(on_message)
c.connect()
c.subscribe(TOPIC_TO)
