import paho.mqtt.client as mqtt
import time
import random

def on_publish(client, userdata, result):
    print("Message published")

client = mqtt.Client("mqttx_device3")
client.on_publish = on_publish

# Set TLS
client.tls_set(ca_certs="path_to_rootCA.crt", certfile=None, keyfile=None)
client.tls_insecure_set(False)  # Set to True for testing if self-signed
client.username_pw_set("103844421", "103844421")
client.connect("rule28.i4t.swin.edu.au", 8883)

base_topic1 = "103844421"
base_topic2 = "public"
topic1 = "air_quality"
topic2 = "polution_rate"
client.loop_start()

while True:
    fake_aq = round(random.uniform(1, 30), 2)
    fake_pr = round(random.uniform(10, 50), 2)

    client.publish(f"{base_topic1}/{topic1}", f"{fake_aq} asi")
    client.publish(f"{base_topic1}/{topic2}", f"{fake_pr} %")
    client.publish(f"{base_topic2}/{topic1}", f"{fake_aq} asi")
    client.publish(f"{base_topic2}/{topic2}", f"{fake_pr} %")

    time.sleep(5)
