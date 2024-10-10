import paho.mqtt.client as mqtt
import sys
import ssl  

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    if rc == 0:
        client.subscribe(topic)
    else:
        print("Connection failed")

def on_message(client, userdata, message):
    payload = message.payload.decode()
    topic = message.topic
    print(f"Received message from topic '{topic}': {payload}")

client = mqtt.Client("mqttx_client")
client.on_connect = on_connect
client.on_message = on_message

# Configure TLS for client communication using certificate chain
client.tls_set(ca_certs="rootCA.crt", 
               certfile="client.crt",  # Client certificate signed by Intermediate CA
               keyfile="client.key",   # Client private key
               tls_version=ssl.PROTOCOL_TLSv1_2)

# Optional: Set to require validation of the server certificate against the given CA file
client.tls_insecure_set(False) 

client.tls_set(ca_certs="mosquitto_server.crt", certfile=None, keyfile=None, tls_version=ssl.PROTOCOL_TLSv1_2)
client.username_pw_set("103844421", "103844421")
client.connect("rule103.caia.swin.edu.au", 8883)

# Subscribe to different topics based on command-line arguments
# Base-topic includes: 103844421 
# Sub-topic-level-1 includes: temperature, humid_rate, air_quality, pulution_rate, wake_up_time, heart_rate 
# Sub-topic-level-2 includes: inside, outside (temperature)

if len(sys.argv) != 2:
    print("Usage: python Client.py <topic>")
    sys.exit(1)

topic = sys.argv[1]

client.loop_forever()
