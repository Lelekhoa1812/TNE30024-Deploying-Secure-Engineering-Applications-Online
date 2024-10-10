import paho.mqtt.client as mqtt
import time
import random

def on_publish(client, userdata, result):
    print("Message published")

client = mqtt.Client("mqttx_device1")
client.on_publish = on_publish

# Set TLS
client.tls_set(ca_certs="path_to_rootCA.crt", certfile=None, keyfile=None)
client.tls_insecure_set(False)  # Set to True for testing if self-signed
client.username_pw_set("103844421", "103844421")
client.connect("rule28.i4t.swin.edu.au", 8883)

base_topic1 = "public/temperature"
base_topic2 = "103844421/temperature"
client.loop_start()

while True:
    fake_temperature_inside = round(random.uniform(15, 30), 2)
    fake_temperature_outside = round(random.uniform(-10, 40), 2)

    client.publish(f"{base_topic1}/inside", f"{fake_temperature_inside} °C")
    client.publish(f"{base_topic1}/outside", f"{fake_temperature_outside} °C")
    client.publish(f"{base_topic2}/inside", f"{fake_temperature_inside} °C")
    client.publish(f"{base_topic2}/outside", f"{fake_temperature_outside} °C")

    time.sleep(5)
