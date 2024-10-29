import paho.mqtt.client as mqtt
import time
import random
import sys
import ssl

# List of medicines and exercises
medicines = ["Aspirin", "Lisinopril", "Atorvastatin", "Metformin", "Amoxicillin", "Omeprazole", "Ibuprofen", "Losartan"]
exercises = ["Walking", "Yoga", "Swimming", "Cycling", "Stretching", "Jogging", "Pilates", "Tai Chi"]

# Callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    # print(f"Connected with result code {rc}")
    if rc == 0 and 'topic' in globals():
        print(f"Subscribing to topic: {topic}")
        client.subscribe(topic)

# Callback for when a message is received on a subscribed topic.
def on_message(client, userdata, message):
    payload = message.payload.decode()
    topic = message.topic
    print(f"Received message from topic '{topic}': {payload}")


# Set up MQTT client
client = mqtt.Client("mqttx_client")
client.on_connect = on_connect
client.on_message = on_message

# Set TLS parameters
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
    # Default action when no topic is provided: Publish health advice topics
    base_topic1 = "103844421/medicine"
    base_topic2 = "103844421/exercise"

    # Randomly choose a medicine and an exercise
    # Assume that health advices only given once a day, therefore data only generated once and keep sending
    chosen_medicine = random.choice(medicines)
    chosen_exercise = random.choice(exercises)

    # Start the loop to manage connections
    client.loop_start()

    # Publishing data in a loop
    while True:
        try:
            # Publish medicine and exercise data to topics
            client.publish(base_topic1, f"Your medicine intake for today is {chosen_medicine}")
            client.publish(base_topic2, f"Your exercise for today is {chosen_exercise}")

            print(f"Your medicine intake for today is {chosen_medicine}")
            print(f"Your exercise for today is {chosen_exercise}")

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

# Publish patient (user) health status data (User):
## public/wake_up_time
## public/heart_rate
## 103844421/wake_up_time
## 103844421/heart_rate

# Usage:
# As a subscriber:
# python3 Client.py <topic>
# As a topic publisher:
# python3 Client.py 