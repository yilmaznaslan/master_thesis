import time
import paho.mqtt.client as mqtt
import json

# TTN Credidentials 
app_id = "tez_test"
dev_id = "tuberlin_lora"
app_access_key = "ttn-account-v2.iClDkXeKp67ziIBLDCIGVbrRSinwRksbcCrff0XgNxg"



# TTN MQTT variables
ttn_server = 'eu.thethings.network'
ttn_port = 1883
ttn_topicTelemetry = app_id+"/"+"devices/"+dev_id+"/up"


# Thingsboard MQTT Variables
thingsboard_server = 'demo.thingsboard.io'
thingsboard_port = 1883
thingsboard_topicTelemetry = "v1/devices/me/telemetry"



def ttn_on_connect(client, userdata, flags, rc):
    global mqtt_return
    mqtt_return = {0: "Connection accepted",
               1: "Connection refused, unacceptable protocol version",
               2: "Connection refused, identifier rejected",
               3: "Connection refused, server unavailable",
               4: "Connection refused, bad user name or password",
               5: "Connection refused, not authorized"}

    cname = client._client_id.decode('utf-8')
    print("Client: {} MQTT return code: {}".format(cname, mqtt_return[rc]))
    client.subscribe(ttn_topicTelemetry)

def ttn_on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection.")

def ttn_on_message(client, userdata, msg):
    global robot1_autopilot, robot2_autopilot
    msg_str = msg.payload.decode('utf-8')
    msg_json = json.loads(msg_str)
    client_id = client._client_id.decode('utf-8')
   
    level_str = json.dumps(msg_json["payload_fields"])
    print("Message received: "+level_str)
    thingsboard_client.publish(thingsboard_topicTelemetry,level_str)
    

def thingsboard_on_connect(client, userdata, flags, rc):
    global mqtt_return
    cname = client._client_id.decode('utf-8')
    print("Client: {} MQTT return code: {}".format(cname, mqtt_return[rc]))
    client.subscribe(ttn_topicTelemetry)
    
def thingsboard_on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection.")

# Create MQTT Connection to TTN
ttn_client = mqtt.Client("TTN_Connector")
ttn_client.username_pw_set(app_id,app_access_key)
ttn_client.on_connect = ttn_on_connect
ttn_client.on_disconnect = ttn_on_disconnect
ttn_client.on_message = ttn_on_message
ttn_client.connect(ttn_server, ttn_port)


# Create MQTT Connection to Thingbsoard
thingsboard_client = mqtt.Client("Thingsboard_TTN_Connector")
thingsboard_client.username_pw_set("ttn_connector")
thingsboard_client.on_connect = thingsboard_on_connect
thingsboard_client.on_disconnect = thingsboard_on_disconnect
#thingsboard_client.on_message = ttn_on_message
thingsboard_client.connect(thingsboard_server, thingsboard_port)
thingsboard_client.loop_start()




ttn_client.loop_forever()
