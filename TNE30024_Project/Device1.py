import paho.mqtt.client as mqtt
import time
import random
import ssl
import sys

# Callback when message is published
def on_publish(client, userdata, result):
    print("Message published")

client = mqtt.Client("mqttx_d1")

# Attach callback function
client.on_publish = on_publish

# Set TLS parameters (CA certificate only)
## PASS
# client.tls_set(ca_certs="crt/pass/server.crt", tls_version=ssl.PROTOCOL_TLSv1_2)
## CREDIT
# client.tls_set(ca_certs="crt/credit/rootCA.crt", tls_version=ssl.PROTOCOL_TLSv1_2)
## DISTINCTION
client.tls_set(ca_certs="crt/distinction/rootCA.crt", tls_version=ssl.PROTOCOL_TLSv1_2)

# Whether the client should accept a certificate without verifying it against the CA. 
# client.tls_insecure_set(True) # PASS and CREDIT
client.tls_insecure_set(False) # DISTINCTION

# Set username and password for authentication
client.username_pw_set("khoa", "103844421")

# Try connecting to the MQTT broker
try:
    client.connect("rule103.i4t.swin.edu.au", 8883)  # Ensure the server (Mosquitto) is running
except Exception as e:
    print(f"Failed to connect: {e}")
    exit(1)

# Topics for publishing data
base_topic1 = "public/temperature"
base_topic2 = "103844421/temperature"

# Start the loop to manage connections
client.loop_start()

# Publishing data in a loop
while True:
    try:
        # Simulating temperature data
        fake_temperature_inside = round(random.uniform(15, 30), 2)
        fake_temperature_outside = round(random.uniform(-10, 40), 2)
        # Publish temperature data to topics
        client.publish(f"{base_topic1}/inside", f"{fake_temperature_inside} °C")
        client.publish(f"{base_topic1}/outside", f"{fake_temperature_outside} °C")
        client.publish(f"{base_topic2}/inside", f"{fake_temperature_inside} °C")
        client.publish(f"{base_topic2}/outside", f"{fake_temperature_outside} °C")
        # Delay before sending the next set of data
        time.sleep(10)

    except KeyboardInterrupt:
        print("Exiting...")
        break
    except Exception as e:
        print(f"Error occurred: {e}")
        break

# Stop the loop when done
client.loop_stop()

# Usage:
# python3 Device1.py 