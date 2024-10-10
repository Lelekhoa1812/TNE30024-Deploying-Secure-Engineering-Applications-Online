import paho.mqtt.client as mqtt
import time
import random
import ssl  

# This device monitoring the temperature in and outside the house (in Celsius degree)
def on_publish(client, userdata, result):
    print("Message published")

client = mqtt.Client("mqttx_device1")
client.on_publish = on_publish

# Configure TLS for Device1 communication using certificate chain
client.tls_set(ca_certs="rootCA.crt", 
               certfile="device1.crt",   # Device1 certificate signed by Intermediate CA
               keyfile="device1.key",    # Device1 private key
               tls_version=ssl.PROTOCOL_TLSv1_2)

# Ensure server certificate is validated
client.tls_insecure_set(False)

client.username_pw_set("103844421", "103844421")
client.connect("rule103.caia.swin.edu.au", 8883)

base_topic1 = "public/temperature"  # Base-topic-public/Sub-topic-level-1
base_topic2 = "103844421/temperature"  # Base-topic-private/Sub-topic-level-1
client.loop_start()

while True:
    fake_temperature_inside = round(random.uniform(15, 30), 2)
    fake_temperature_outside = round(random.uniform(-10, 40), 2)

    # Publish temperature data to corresponding to the Sub-topic-level-2
    client.publish(f"{base_topic1}/inside", f"{fake_temperature_inside} °C")  
    client.publish(f"{base_topic1}/outside", f"{fake_temperature_outside} °C")  
    client.publish(f"{base_topic2}/inside", f"{fake_temperature_inside} °C")  
    client.publish(f"{base_topic2}/outside", f"{fake_temperature_outside} °C")  

    time.sleep(5)
