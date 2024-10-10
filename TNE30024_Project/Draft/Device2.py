import paho.mqtt.client as mqtt
import time
import random
import ssl

# This device monitoring the humidity outside the house (in percentage %)
def on_publish(client, userdata, result):
    print("Message published")

client = mqtt.Client("mqttx_device2")
client.on_publish = on_publish

# Configure TLS for Device2 communication using certificate chain
client.tls_set(ca_certs="rootCA.crt", 
               certfile="device2.crt",   # Device2 certificate signed by Intermediate CA
               keyfile="device2.key",    # Device2 private key
               tls_version=ssl.PROTOCOL_TLSv1_2)

# Ensure server certificate is validated
client.tls_insecure_set(False)

client.username_pw_set("103844421", "103844421")
client.connect("rule103.caia.swin.edu.au", 8883)

topic1 = "103844421/humid_rate"  # Base-topic-private/Sub-topic-level-1
topic2 = "public/humid_rate"  # Base-topic-public/Sub-topic-level-1
client.loop_start()

while True:
    fake_humidity = round(random.uniform(20, 80), 2)
    client.publish(topic1, f"{fake_humidity} %")
    client.publish(topic2, f"{fake_humidity} %")

    time.sleep(5)
