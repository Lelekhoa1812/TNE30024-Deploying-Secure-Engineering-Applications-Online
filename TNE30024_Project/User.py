import paho.mqtt.client as mqtt
import time
import random
import sys
import ssl

# Callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    # print(f"Connected with result code {rc}")
    if rc == 0 and 'topic' in globals():
        # Subscribe to the provided topic if passed via command-line arguments
        print(f"Subscribing to topic: {topic}")
        client.subscribe(topic)

# Callback for when a message is received on a subscribed topic.
def on_message(client, userdata, message):
    payload = message.payload.decode()
    topic = message.topic
    print(f"Received message from topic '{topic}': {payload}")

client = mqtt.Client("mqttx_user")
# Set callback functions
client.on_connect = on_connect
client.on_message = on_message

# Set TLS parameters (CA certificate only, assuming no client certs required)
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

# Try to connect to the MQTT broker (Mosquitto server)
try:
    client.connect("rule103.i4t.swin.edu.au", 8883)
except Exception as e:
    print(f"Failed to connect: {e}")
    sys.exit(1)

# Check if a topic was provided via command-line arguments
if len(sys.argv) > 1:
    topic = sys.argv[1]
    client.loop_forever()  # Loop forever, receiving messages on the subscribed topic
else:
    # Start the loop to manage connections
    client.loop_start()

    # Default action when no topic is provided: Publish health status topics
    # Assume that health status only recorded once a day, therefore data only generated once and keep sending
    base_topic = "103844421"
    topic1 = "wake_up_time"
    fake_wut = f"{random.randint(4, 10)}:{random.randint(0, 5)}{random.randint(0, 9)} AM"
    topic2 = "heart_rate"
    fake_ht = f"{round(random.uniform(40, 140), 2)} bpm"
    
# Publishing data in a loop
    while True:
        try:
            # Publish simulated wake-up time as a sub-topic-level-1
            print(f"Today wake-up time is: {fake_wut}")
            client.publish(f"{base_topic}/{topic1}", fake_wut)

            # Publish simulated heart rate as a sub-topic-level-1
            print(f"Today heart rate is: {fake_ht}")
            client.publish(f"{base_topic}/{topic2}", str(fake_ht))

            # Delay before sending the next set of data
            time.sleep(5)
        
        # Break
        except KeyboardInterrupt:
            print("Exiting...")
            break
        except Exception as e:
            print(f"Error occurred: {e}")
            break

# List of topics:
# Publish temperature data (Device 1):
## public/temperature/inside
## public/temperature/outside
## 103844421/temperature/inside
## 103844421/temperature/outside

# Publish humidity data (Device 2):
## public/humid_rate
## 103844421/humid_rate

# Publish air quality and pollution data (Device 3):
## public/air_quality
## public/polution_rate
## 103844421/air_quality
## 103844421/polution_rate

# Publish air quality and pollution data (Device 3):
## public/air_quality
## public/polution_rate
## 103844421/air_quality
## 103844421/polution_rate

# Publish doctor/caregiver notice (client) data (Client):
## public/medicine
## public/exercise
## 103844421/medicine
## 103844421/exercise

# Usage:
# As a subscriber:
# python3 User.py <topic>
# As a topic publisher:
# python3 User.py 