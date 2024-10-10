**1. Reconfiguring Mosquitto Server to Support Encrypted Communications**
**1.1 Set Up the Required Configuration Files on the Rule Host**
```
# Create directory for Mosquitto configuration
mkdir -p /usr/local/etc/mosquitto

# Copy mosquitto.conf and aclfile to the correct location
cp config/mosquitto.conf /usr/local/etc/mosquitto/mosquitto.conf
cp config/aclfile /usr/local/etc/mosquitto/aclfile
```

**1.2 Create a Password File**
```
# Create the password file
echo "username:password" > /usr/local/etc/mosquitto/pwfile

# Hash the password file
mosquitto_passwd -U /usr/local/etc/mosquitto/pwfile
```

**1.3 Create the Log Directory**
```
# Create log directory
sudo mkdir /var/log/mosquitto
```

**1.4 Enable and Start Mosquitto Service**  
Ensure Mosquitto is enabled and running on startup. Add the following line to /etc/rc.conf:  
```
# Write new file
sudo vi /etc/rc.conf
```
With content
mosquitto_enable="YES"  
```
# Start Mosquitto
/usr/local/etc/rc.d/mosquitto start

# If restarting is needed
/usr/local/etc/rc.d/mosquitto restart
```  
```
# Verify Mosquitto is Running:
ps aux | grep mosquitto

# Check the status:
sudo service mosquitto status
```

**2. Securing Communications with TLS (Certificates)**
**2.1 Generate a Self-Signed Certificate (For Pass Grade)**
```
# Generate server private key
openssl genrsa -out /usr/local/etc/mosquitto/server.key 2048

# Generate self-signed certificate
openssl req -new -x509 -key /usr/local/etc/mosquitto/server.key -out /usr/local/etc/mosquitto/server.crt -days 365 -subj "/C=AU/ST=State/O=Organization/CN=rule28.i4t.swin.edu.au"
```

**2.2 Configure Mosquitto for TLS**
Edit the mosquitto.conf file to include the paths to the certificate and key:  
```
listener 8883
cafile /usr/local/etc/mosquitto/server.crt
certfile /usr/local/etc/mosquitto/server.crt
keyfile /usr/local/etc/mosquitto/server.key
require_certificate true
allow_anonymous false
password_file /usr/local/etc/mosquitto/pwfile
acl_file /usr/local/etc/mosquitto/aclfile
```

**2.3 Create Certificate Chain (For Credit and Distinction Grades)**
**2.3.1 Create Root CA**
```
# Generate root private key
openssl genrsa -out rootCA.key 2048

# Generate root certificate
openssl req -x509 -new -nodes -key rootCA.key -sha256 -days 1024 -out rootCA.crt -subj "/C=AU/ST=VIC/O=Khoa/CN=RootCA"
```

**2.3.2 Generate Server Certificate Signed by Root CA**
```
# Generate server private key
openssl genrsa -out server.key 2048

# Create server CSR
openssl req -new -key server.key -out server.csr -subj "/C=AU/ST=VIC/O=Khoa/CN=rule28.i4t.swin.edu.au"

# Sign the CSR with root CA
openssl x509 -req -in server.csr -CA rootCA.crt -CAkey rootCA.key -CAcreateserial -out server.crt -days 500 -sha256
```

**2.3.3 Create Certificate Chain (For Distinction Grade)**
**a. Create Intermediate CA**
```
# Generate intermediate private key
openssl genrsa -out intermediateCA.key 2048

# Create intermediate CSR
openssl req -new -key intermediateCA.key -out intermediateCA.csr -subj "/C=AU/ST=VIC/O=Khoa/CN=IntermediateCA"

# Sign intermediate CSR with root CA
openssl x509 -req -in intermediateCA.csr -CA rootCA.crt -CAkey rootCA.key -CAcreateserial -out intermediateCA.crt -days 500 -sha256
```

**b. Generate Mosquitto Server Certificate Signed by Intermediate CA**
```
# Generate server private key
openssl genrsa -out server.key 2048

# Create server CSR
openssl req -new -key server.key -out server.csr -subj "/C=AU/ST=VIC/O=Khoa/CN=rule28.i4t.swin.edu.au"

# Sign the CSR with intermediate CA
openssl x509 -req -in server.csr -CA intermediateCA.crt -CAkey intermediateCA.key -CAcreateserial -out server.crt -days 500 -sha256
```

**c. Create Full Chain Concatenate the server, intermediate, and root certificates.**
```
cat server.crt intermediateCA.crt rootCA.crt > fullchain.crt
```
Update mosquitto.conf to use the full chain.  
listener 8883  
cafile /usr/local/etc/mosquitto/rootCA.crt  
certfile /usr/local/etc/mosquitto/fullchain.crt  
keyfile /usr/local/etc/mosquitto/server.key  
require_certificate true  

Restart Mosquitto after updating the config.  


**3. Modify Python Programs for TLS**
**3.1 Update Python Clients to Use TLS**
In each Python file that uses MQTT (e.g., Client.py, User.py, Device1.py, etc.), modify the connection to use TLS.  

```
client.tls_set(ca_certs="path_to_rootCA.crt", certfile=None, keyfile=None)
client.tls_insecure_set(False)
client.connect("rule28.i4t.swin.edu.au", 8883)
```

**3.2 Update Python Code for Certificate Chain (Distinction)**
Update the Python code to handle certificate chain verification:  
```
client.tls_set(ca_certs="path_to_rootCA.crt", certfile="path_to_client_cert.crt", keyfile="path_to_client_key.key")
client.tls_insecure_set(False)
client.connect("rule28.i4t.swin.edu.au", 8883)
```

**4. Start MQTTX**
```
/usr/local/etc/rc.d/mosquitto start
```