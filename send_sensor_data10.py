#!/usr/bin/env python3
# This is main python file for Facebook Likes monitor project. there is not other file required.
# This file Send  Likes and  Grove sensors  data (Temperature, Light ) periodically to AWS IoT.
# This  file has 3 main functions 
#  1. Getting Likes from particualr page  
#  2. Updating the browser 
#  3. Uploading the sensor data + Likes to AWS IoT/Sumologic /Slack
# Thurday afternoon_final chaned to version 10
# Updated by chandra sekar / chandra@fastmail.net 


import time
import datetime
import ssl
import json
import paho.mqtt.client as mqtt
import grovepi
from selenium import webdriver
import selenium
import json
import webbrowser



try:
    import urllib.request as urllib2
except ImportError:
    import urllib2
import time
from grovepi import *


# TODO: Change this to the name of our Raspberry Pi, also known as our "Thing Name"
deviceName = "g88pi"

# Public certificate of our Raspberry Pi, as provided by AWS IoT.
deviceCertificate = "tp-iot-certificate.pem.crt"
# Private key of our Raspberry Pi, as provided by AWS IoT.
devicePrivateKey = "tp-iot-private.pem.key"
# Root certificate to authenticate AWS IoT when we connect to their server.
awsCert = "aws-iot-rootCA.crt"

isConnected = False
Like = 0  ##  Added this.  Must initialise.
tempL = 0  ##  Added this.  Must initialise.
global access_token

# Assume we connected the Grove Light Sensor to analog port A0,
# Digital Humidity/Temperature Sensor (DHT11) to digital port D2,
# Sound Sensor to A2, Grove LED to digital port D4.
# If you are using the Grove Analog Temperature Sensor, connect it to analog port A1.
light_sensor = 0
#sound_sensor = 2
dht_sensor = 2
led = 4
pinMode (led,"OUTPUT")
time.sleep(5)
buzzer = 8
grovepi.pinMode(buzzer,"OUTPUT")
temp_sensor = 1
# Function to get  Likes from FACEBOOK page 
def get_page_data(page_id, access_token):  ##  Moved this
    global Like  ##  Added this
    # Add a random suffix to prevent caching
    random_suffix = "&random=" + datetime.datetime.now().isoformat()
    api_endpoint = "https://graph.facebook.com/v2.4/"
    fb_graph_url = api_endpoint + page_id + "?fields=id,name,likes,link&access_token=" + access_token + random_suffix
    print("fb_graph_url=" + fb_graph_url)

    try:
        api_request = urllib2.Request(fb_graph_url)
        api_response = urllib2.urlopen(api_request)

        try:
            result = api_response.read()
            result_str = str(result.decode("utf-8"))
            print(result_str)
            return json.loads(result_str)
        except (ValueError, KeyError, TypeError) as e:
            print("JSON error: " + str(e))
            return "JSON error"
    except IOError as e:
        print("IOError: " + str(e))
        if hasattr(e, 'code'):
            return e.code
        elif hasattr(e, 'reason'):
            return e.reason

page_id = "783256781810074"  # username or id
token = "EAACEdEose0cBAIKUquFylMqRe2KcQxBrbjP53yFErfqYXOV4kwWxFhDAp51xyGYwvVpjtkAaLj8mx0iZC59pK6FuFTLc1Hr45aF6D8ssqMd8iN3kdPCZCSsXomNkqF1v3OUVZCKDQQhRK11bQlmEIqwAvZAakslXZBrnqMXkLthquuyEXrCOZC" # Access Token

#page_data = get_page_data(page_id, token)
#page_data = get_page_data(page_id, access_token)
# print ("Page Name:")+str(page_data['name'])
#print("Likes:" + str(page_data['likes']))

driver = webdriver.Firefox()
driver.get("https://www.facebook.com/plugins/fan.php?connections=100&id=783256781810074")
driver.refresh()


# This is the main logic of the program.  We connect to AWS IoT via MQTT, send sensor data periodically to AWS IoT,
# and handle any actuation commands received from AWS IoT.
def main():
    global isConnected
    global Like
    global tempL  ##  Added this
    # Create an MQTT client for connecting to AWS IoT via MQTT.
    client = mqtt.Client(deviceName + "_sr")  # Client ID must be unique because AWS will disconnect any duplicates.
    client.on_connect = on_connect  # When connected, call on_connect.
    client.on_message = on_message  # When message received, call on_message.
    client.on_log = on_log  # When logging debug messages, call on_log.

    # Set the certificates and private key for connecting to AWS IoT.  TLS 1.2 is mandatory for AWS IoT and is supported
    # only in Python 3.4 and later, compiled with OpenSSL 1.0.1 and later.
    client.tls_set(awsCert, deviceCertificate, devicePrivateKey, ssl.CERT_REQUIRED, ssl.PROTOCOL_TLSv1_2)

    # Connect to AWS IoT server.  Use AWS command line "aws iot describe-endpoint" to get the address.
    print("Connecting to AWS IoT...")

    client.connect("A1P01IYM2DOZA0.iot.us-west-2.amazonaws.com", 8883, 60)

    # Start a background thread to process the MQTT network commands concurrently, including auto-reconnection.
    client.loop_start()

    # Configure the Grove LED port for output.
    grovepi.pinMode(led, "OUTPUT")
    time.sleep(1)


    # Loop forever.
    while True:

            # If we are
        try:
            # if not connected yet to AWS IoT, wait 1 second and try again.
            if not isConnected:
                time.sleep(4)
                continue

            # check for likes
            print("Getting likes...")
            page_data = get_page_data(page_id, token)
            Like = str(page_data['likes'])
            print("Likes: " + Like)

            if int(Like) > 0  and int(Like)>  int(tempL):

                print(tempL)
                print("Inside if -success 1")
                # Buzz for 1 second
                grovepi.digitalWrite(buzzer,1)
                print ('start')
                time.sleep(1)

        # Stop buzzing for 1 second and repeat
                grovepi.digitalWrite(buzzer,0)
                print ('stop')
                time.sleep(1)
                digitalWrite(led, 1)  # Send HIGH to switch on LED
                time.sleep(10)
                digitalWrite(led, 0)  # Send HIGH to switch on LED
                tempL = Like
            #elif (int(Like) = int(tempL)):
              #  #tempL = int(Like) + int(1)
                #print(tempL)
                #print("Inside if -success 2")
                #digitalWrite(led, 1)  # Send HIGH to switch on LED
                #time.sleep(10)
                #digitalWrite(led, 0)  # Send HIGH to switch on LED

            else:
                print(" not inside if -not success")
                digitalWrite(led, 0)  # Send LOW to switch off LED
                print(tempL)
                time.sleep(5)

            # Read Grove sensor values. Prepare our sensor data in JSON format.
            payload = {
                "state": {
                    "reported": {
                        # Uncomment the next line if you're using the Grove Analog Temperature Sensor.
                         "temperature": round(grovepi.temp(temp_sensor, '1.1'), 1),
                        # Comment out the next 2 lines if you're using the Grove Analog Temperature Sensor.
                       # "temperature": grovepi.dht(dht_sensor, 0)[0],  # The first 0 means that the DHT module is DHT11.
                        #####"humidity": grovepi.dht(dht_sensor, 0)[1],
                        "light_level": grovepi.analogRead(light_sensor),
                        #####"sound_level": grovepi.analogRead(sound_sensor),
                        "Likes":Like,
                        "timestamp": datetime.datetime.now().isoformat()

                    }
                }
            }
            print("Sending sensor data to AWS IoT...\n" +
                  json.dumps(payload, indent=4, separators=(',', ': ')))

            # Publish our sensor data to AWS IoT via the MQTT topic, also known as updating our "Thing Shadow".
            client.publish("$aws/things/" + deviceName + "/shadow/update", json.dumps(payload))
            print("Sent to AWS IoT")
            driver.refresh()
            # Wait 30 seconds before sending the next set of sensor data.
            #schedule.run_pending()
            time.sleep(30)

        except KeyboardInterrupt:
            break
        except Exception as e:
            # For all other errors, we wait a while and resume.
            print("Exception: " + str(e))
            time.sleep(10)
            continue

# This is called when we are connected to AWS IoT via MQTT.
# We subscribe for notifications of desired state updates.
def on_connect(client, userdata, flags, rc):
    global isConnected
    isConnected = True
    print("Connected to AWS IoT")
    # Subscribe to our MQTT topic so that we will receive notifications of updates.
    topic = "$aws/things/" + deviceName + "/shadow/update/accepted"
    print("Subscribing to MQTT topic " + topic)
    client.subscribe(topic)
    #driver = webdriver.Firefox()
    #driver.get("https://www.facebook.com/plugins/fan.php?connections=100&id=783256781810074")
    driver.refresh()

# This is called when we receive a subscription notification from AWS IoT.
def on_message(client, userdata, msg):
    # Convert the JSON payload to a Python dictionary.
    # The payload is in binary format so we need to decode as UTF-8.
    payload2 = json.loads(msg.payload.decode("utf-8"))
    print("Received message, topic: " + msg.topic + ", payload:\n" +
          json.dumps(payload2, indent=4, separators=(',', ': ')))


# Print out log messages for tracing.
def on_log(client, userdata, level, buf):
    print("Log: " + buf)

if __name__ == "__main__":
    # Start the main program
    main()
