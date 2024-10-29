import paho.mqtt.client as mqtt
import time
import random
import sys
import ssl

# Callback for publishing messages
def on_publish(client, userdata, result):
    print("Message published")

# Create a new MQTT client instance
client = mqtt.Client("mqttx_d3")
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

# Topics for publishing air quality and pollution data
base_topic1 = "103844421"
base_topic2 = "public"
topic1 = "air_quality"
topic2 = "polution_rate"

# Start the MQTT client loop
client.loop_start()

# Publishing air quality and pollution data in a loop
while True:
    try:
        fake_aq = round(random.uniform(1, 30), 2)
        fake_pr = round(random.uniform(10, 50), 2)
        client.publish(f"{base_topic1}/{topic1}", f"{fake_aq} asi")
        client.publish(f"{base_topic1}/{topic2}", f"{fake_pr} %")
        client.publish(f"{base_topic2}/{topic1}", f"{fake_aq} asi")
        client.publish(f"{base_topic2}/{topic2}", f"{fake_pr} %")
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
# python3 Device3.py 