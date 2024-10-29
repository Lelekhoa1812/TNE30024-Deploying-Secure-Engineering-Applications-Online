import tkinter as tk
from tkinter import ttk
import paho.mqtt.client as mqtt
import time
import ssl
import random

# =======================
# SETUPS
# =======================

# MQTT client instance (global)
client = mqtt.Client("mqttx_user")

# Callback for when the client connects to the broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        display_data("System", "Connected to MQTT broker.")
    else:
        display_data("System", "Failed to connect to MQTT broker.")

# Callback for when a message is received
def on_message(client, userdata, message):
    payload = message.payload.decode()
    topic = message.topic
    display_data(topic, payload)

# Display data in the Text widget
def display_data(topic, data):
    data_text.config(state=tk.NORMAL)
    data_text.insert(tk.END, f"Topic: {topic}\nData: {data}\n\n")
    data_text.config(state=tk.DISABLED)

# Subscribe to a new topic
def subscribe_topic():
    new_topic = topic_entry.get()
    if new_topic:
        display_data("System", f"Subscribing to topic: {new_topic}")
        client.subscribe(new_topic)

# Setup and configure MQTT connection
def setup_mqtt():
    client.on_connect = on_connect
    client.on_message = on_message

    # Set TLS for secure connection
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

    # Connect to the broker
    client.connect("rule103.i4t.swin.edu.au", 8883)

    # Start the MQTT client loop in a background thread
    client.loop_start()

# Post Wake Up Time and Heart Rate
def post_data():
    base_topic = "103844421"
    wake_up_time_topic = f"{base_topic}/wake_up_time"
    heart_rate_topic = f"{base_topic}/heart_rate"

    wake_up_time = wake_up_time_entry.get()
    heart_rate = heart_rate_entry.get()

    if wake_up_time:
        client.publish(wake_up_time_topic, wake_up_time)
        display_data("System", f"Published wake-up time: {wake_up_time}")
    
    if heart_rate:
        client.publish(heart_rate_topic, heart_rate)
        display_data("System", f"Published heart rate: {heart_rate} bpm")

# Initialize the tkinter GUI
root = tk.Tk()
root.title("MQTT Client Interface")

# Create a Notebook for the tabbed interface
notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill="both")

# =======================
# Monitor Tab (Subscribe and View Messages)
# =======================
# Create the frame for the "Monitor" tab, where users can subscribe to topics and view incoming messages
monitor_frame = ttk.Frame(notebook)
notebook.add(monitor_frame, text="Monitor") # label tab

# Instruction
topic_label = ttk.Label(monitor_frame, text="Enter Topic to Subscribe:")
topic_label.pack(pady=10)

# Entry field text-holder
topic_entry = ttk.Entry(monitor_frame, width=40)
topic_entry.pack(pady=5)

# Subscribe button, when pressed, trigger 'subscribe_topic' function to subscribe to the topic
subscribe_button = ttk.Button(monitor_frame, text="Subscribe", command=subscribe_topic)
subscribe_button.pack(pady=5)

# Text area to display incoming MQTT messages after subscribing to the topic
data_text = tk.Text(monitor_frame, wrap=tk.WORD, width=50, height=20)
data_text.config(state=tk.DISABLED)
data_text.pack(pady=10)

# =======================
# Post Tab (Publish Data)
# =======================
# Create the frame for the "Post" tab, where users can publish their health data (Wake Up Time, Heart Rate)
post_frame = ttk.Frame(notebook)
notebook.add(post_frame, text="Post") # label tab

# Instruction
wake_up_time_label = ttk.Label(post_frame, text="Enter Wake Up Time:")
wake_up_time_label.pack(pady=10)

# Entry field text-holder
wake_up_time_entry = ttk.Entry(post_frame, width=40)
wake_up_time_entry.pack(pady=5)

# Instruction
heart_rate_label = ttk.Label(post_frame, text="Enter Heart Rate (in bpm):")
heart_rate_label.pack(pady=10)

# Entry field text-holder
heart_rate_entry = ttk.Entry(post_frame, width=40)
heart_rate_entry.pack(pady=5)

# Post Data button, when pressed, trigger 'post_data' function to post the data with the topic
post_button = ttk.Button(post_frame, text="Post Data", command=post_data)
post_button.pack(pady=10)

# Setup MQTT connection
setup_mqtt()

# Run the tkinter GUI loop
root.mainloop()
