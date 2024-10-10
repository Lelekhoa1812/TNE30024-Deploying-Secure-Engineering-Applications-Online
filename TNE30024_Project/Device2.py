import paho.mqtt.client as mqtt
import time
import random

def on_publish(client, userdata, result):
    print("Message published")

client = mqtt.Client("mqttx_device2")
client.on_publish = on_publish

# Set TLS
client.tls_set(ca_certs="path_to_rootCA.crt", certfile=None, keyfile=None)
client.tls_insecure_set(False)  # Set to True for testing if self-signed
client.username_pw_set("103844421", "103844421")
client.connect("rule28.i4t.swin.edu.au", 8883)

topic1 = "103844421/humid_rate"
topic2 = "public/humid_rate"
client.loop_start()

while True:
    fake_humidity = round(random.uniform(20, 80), 2)
    client.publish(topic1, f"{fake_humidity} %")
    client.publish(topic2, f"{fake_humidity} %")

    time.sleep(5)
