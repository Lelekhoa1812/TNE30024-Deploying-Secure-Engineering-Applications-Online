import paho.mqtt.client as mqtt
import time
import random
import sys
import ssl

# Callback for publishing messages
def on_publish(client, userdata, result):
    print("Message published")

# Create a new MQTT client instance
client = mqtt.Client("mqttx_d2")
client.on_publish = on_publish

# Set TLS
## PASS
# client.tls_set(ca_certs="crt/pass/server.crt", tls_version=ssl.PROTOCOL_TLSv1_2)
## CREDIT
# client.tls_set(ca_certs="crt/credit/rootCA.crt", tls_version=ssl.PROTOCOL_TLSv1_2)
## DISTINCTION
client.tls_set(ca_certs="crt/distinction/rootCA.crt", certfile=None, keyfile=None)

# Whether the client should accept a certificate without verifying it against the CA. 
# client.tls_insecure_set(True) # PASS and CREDIT
client.tls_insecure_set(False) # DISTINCTION

# Set username and password for authentication
client.username_pw_set("khoa", "103844421")

# Connect to the MQTT broker
try:
    client.connect("rule103.i4t.swin.edu.au", 8883)
except Exception as e:
    print(f"Failed to connect: {e}")
    sys.exit(1)

# Topics for publishing humidity data
topic1 = "103844421/humid_rate"
topic2 = "public/humid_rate"

# Start the MQTT client loop
client.loop_start()

# Publishing humidity data in a loop
while True:
    try:
        fake_humidity = round(random.uniform(20, 80), 2)
        client.publish(topic1, f"{fake_humidity} %")
        client.publish(topic2, f"{fake_humidity} %")
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
# python3 Device2.py 