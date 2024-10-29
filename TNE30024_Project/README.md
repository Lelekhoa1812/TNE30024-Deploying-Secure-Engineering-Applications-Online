**Log in to Rule host**
```
ssh student@136.186.230.103
(student@136.186.230.103) Password for student@rule103: ggtm4lma
```
Vi bash essentials:   
- d + right - delete 1 char of the cursor
- d + left - delete 1 char to the left of cursor
- shift + left/right - delete line
- :q! - delete override
- :wd! - save override
- /password_file - search for password file (change variable to search for)

## 1. Reconfiguring Mosquitto Server to Support Encrypted Communications**
**1.1 Set Up the Required Configuration Files on the Rule Host**
```
# Create directory for Mosquitto configuration (if not there) 
mkdir -p /usr/local/etc/mosquitto

# From local machine, copy mosquitto.conf and aclfile to the correct location in Rule host's home directory
scp ~/Downloads/TNE30024/TNE30024_Project/config/mosquitto.conf ~/Downloads/TNE30024/TNE30024_Project/config/aclfile student@136.186.230.103:~

# Be a super user first
su
Password: cbv6eqm7

# Move the files to /usr/local/etc/mosquitto/
mv mosquitto.conf /usr/local/etc/mosquitto/mosquitto.conf
mv aclfile /usr/local/etc/mosquitto/aclfile

# Optional: ls to confirm action success
```

**1.2 mosquitto.connf**
Optional: Examine the example file  
vi /usr/local/etc/mosquitto/mosquitto.conf.sample  

# Change file
vi /usr/local/etc/mosquitto/mosquitto.conf  
```
listener 8883

## FOR PASS
cafile /usr/local/etc/mosquitto/pass/server.crt
certfile /usr/local/etc/mosquitto/pass/server.crt
keyfile /usr/local/etc/mosquitto/pass/server.key

## FOR CREDIT
cafile /usr/local/etc/mosquitto/credit/server.crt
certfile /usr/local/etc/mosquitto/credit/server.crt
keyfile /usr/local/etc/mosquitto/credit/server.key

## FOR DISTINCTION
cafile /usr/local/etc/mosquitto/distinction/rootCA.crt
certfile /usr/local/etc/mosquitto/distinction/fullchain.crt
keyfile /usr/local/etc/mosquitto/distinction/server.key

require_certificate false
allow_anonymous false
tls_version tlsv1.2

acl_file /usr/local/etc/mosquitto/aclfile
password_file /usr/local/etc/mosquitto/pwfile
log_dest file /var/log/mosquitto/mosquitto.log
log_type all
log_timestamp true
```

**1.3 Create a Password File**
```
# Create the password file
echo "khoa:103844421" > /usr/local/etc/mosquitto/pwfile

# Hash the password file
mosquitto_passwd -U /usr/local/etc/mosquitto/pwfile
```

**1.4 Create the Log Directory**  
Create log directory  
```
mkdir /var/log/mosquitto
```

**1.5 aclfile**   
vi /usr/local/etc/mosquitto/mosquitto.conf   
```
pattern readwrite %u/#
pattern readwrite public/#
####
user admin
topic readwrite #
####
user khoa
topic readwrite 103844421/#
```

**1.6 rc.conf**
```
# Navigate
vi /etc/rc.conf

# Allow mosquitto
mosquitto_enable="YES"
```

**1.7 Start/Stop/Restart Mosquitto Service**  
```
/usr/local/etc/rc.d/mosquitto start
/usr/local/etc/rc.d/mosquitto stop
/usr/local/etc/rc.d/mosquitto restart
```

**1.8 Debugs**
```
mkdir -p /var/log/mosquitto
touch /var/log/mosquitto/mosquitto.log
chmod 666 /var/log/mosquitto/mosquitto.log
chmod 644 /usr/local/etc/mosquitto/server.key
chmod 644 /usr/local/etc/mosquitto/fullchain.crt
chown mosquitto:mosquitto /usr/local/etc/mosquitto/server.key
chown mosquitto:mosquitto /usr/local/etc/mosquitto/fullchain.crt
chmod 640 /usr/local/etc/mosquitto/pwfile
chown mosquitto:mosquitto /usr/local/etc/mosquitto/pwfile
```


## 2. Securing Communications with TLS (Certificates)**
Navigate to correct dir first:  
```
cd /usr/local/etc/mosquitto/ 
```
Split to different task directories:
```
mkdir pass
mkdir credit
mkdir distinction
```
# PASS
**2.1 Generate a Self-Signed Certificate**
```
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /usr/local/etc/mosquitto/pass/server.key -out /usr/local/etc/mosquitto/pass/server.crt -subj "/C=AU/ST=VIC/O=Khoa/CN=rule103.i4t.swin.edu.au"
```
# CREDIT
**2.2 Create Certificate Chain**
**2.2.1 Create Root CA**
```
# Generate root private key
openssl genrsa -out rootCA.key 2048

# Generate root certificate
openssl req -x509 -new -nodes -key rootCA.key -sha256 -days 1024 -out rootCA.crt -subj "/C=AU/ST=VIC/O=Khoa/CN=RootCA"
```
**2.2.2 Generate Server Certificate Signed by Root CA**
```
# Generate server private key
openssl genrsa -out server.key 2048

# Create server CSR
openssl req -new -key server.key -out server.csr -subj "/C=AU/ST=VIC/O=Khoa/CN=rule103.i4t.swin.edu.au"

# Sign the CSR with root CA
openssl x509 -req -in server.csr -CA rootCA.crt -CAkey rootCA.key -CAcreateserial -out server.crt -days 500 -sha256
```

# DISTINCTION
**2.3 Create Certificate Chain**
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
openssl req -new -key server.key -out server.csr -subj "/C=AU/ST=VIC/O=Khoa/CN=rule103.i4t.swin.edu.au"

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
openssl req -new -key server.key -out server.csr -subj "/C=AU/ST=VIC/O=Khoa/CN=rule103.i4t.swin.edu.au"

# Sign the CSR with intermediate CA
openssl x509 -req -in server.csr -CA intermediateCA.crt -CAkey intermediateCA.key -CAcreateserial -out server.crt -days 500 -sha256
```
**c. Create Full Chain Concatenate the server, intermediate, and root certificates.**
```
cat server.crt intermediateCA.crt rootCA.crt > fullchain.crt
```
**d. Download all crt, csr, key etc to local machine, suggest to use CyberDuck (MacOS)**
Grant user access first to download key files:  
```
chmod 644 server.key
chmod 644 rootCA.key
chmod 644 intermediateCA.key
```
Then download the 'pass', 'credit', and 'distinction' folder to the machine under 'crt' directory.

## 3. Modify Python Programs for TLS**
# PASS
**3.1 Modify Python Programs to Support TLS with Self-Signed Certificate**
In each Python file that uses MQTT (e.g., Client.py, User.py, Device1.py, etc.), modify the connection to use TLS.  
```
client.tls_set(ca_certs="crt/pass/server.crt", tls_version=ssl.PROTOCOL_TLSv1_2)
client.tls_insecure_set(True)  # Allows connection to self-signed certificate
client.username_pw_set("username", "password")
client.connect("rule103.i4t.swin.edu.au", 8883)
client.loop_start()
```
# CREDIT
**3.2 Modify Python Programs to Use the CA-Signed Certificate**
```
client.tls_set(ca_certs="crt/credit/rootCA.crt", tls_version=ssl.PROTOCOL_TLSv1_2)
client.tls_insecure_set(False)  # Requires CA-signed certificates
client.username_pw_set("username", "password")
client.connect("rule103.i4t.swin.edu.au", 8883)
client.loop_start()
```
# DISTINCTION
**3.3 Update Python Code for Certificate Chain (Distinction)**
Update the Python code to handle certificate chain verification:  
```
client.tls_set(ca_certs="crt/distinction/rootCA.crt", tls_version=ssl.PROTOCOL_TLSv1_2)
client.tls_insecure_set(TRUE)
client.connect("rule103.i4t.swin.edu.au", 8883)
```

## 4. Start MQTTX**
```
/usr/local/etc/rc.d/mosquitto start
```

## 5. Move python scripts to rulehost (Optional, not necessary)**
```
scp ~/Downloads/TNE30024/TNE30024_Project/Client.py ~/Downloads/TNE30024/TNE30024_Project/User.py ~/Downloads/TNE30024/TNE30024_Project/Device1.py ~/Downloads/TNE30024/TNE30024_Project/Device2.py ~/Downloads/TNE30024/TNE30024_Project/Device3.py student@136.186.230.103:~
```

```
mv /usr/home/student/Client.py /usr/home/student/User.py /usr/home/student/Device1.py /usr/home/student/Device2.py /usr/home/student/Device3.py usr/local/etc/mosquitto
```

## 6. Run devices, user and client**
```
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

# Publish doctor/caregiver notice (client) data (Client):
## public/medicine
## public/exercise
## 103844421/medicine
## 103844421/exercise

# Usage:
# As a subscriber:
python3 Client.py <topic>
python3 User.py <topic>
# As a topic publisher:
python3 Client.py 
python3 User.py 
# Devices:
python3 Device1.py
python3 Device2.py
python3 Device3.py
```