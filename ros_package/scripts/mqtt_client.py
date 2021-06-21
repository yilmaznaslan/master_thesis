#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import rospy
import json
import time
from std_msgs.msg import String
mqtt_server = 'demo.thingsboard.io'
mqtt_port = 1883
topicTelemetry = "v1/devices/me/telemetry"
topicAttribute = "v1/devices/me/attributes"
mqtt_return = {0: "Connection accepted",
               1: "Connection refused, unacceptable protocol version",
               2: "Connection refused, identifier rejected",
               3: "Connection refused, server unavailable",
               4: "Connection refused, bad user name or password",
               5: "Connection refused, not authorized"}
robot_username = "Robot1"
client = mqtt.Client(robot_username)
pub = None


def init_node():
    global pub
    rospy.init_node('mqtt_connection', anonymous=True)
    pub = rospy.Publisher('veh_error', String, queue_size=100)
    print("ROS Node initialized")
    rospy.spin()


def handle_dummy_error(payload):
    # This is used in the simulation. If a dummy error is initated
    # from the user panel, it will be shared with ROS. In a normal
    # operation there is no need to use this function.
    payload_json = json.loads(payload)
    if(payload_json["simulate_error"] == 1):
        pub.publish("error_on")
    if(payload_json["simulate_error"] == 0):
        pub.publish("error_off")


def init_mqtt():
    global client
    client = mqtt.Client(robot_username)
    client.username_pw_set(robot_username)
    client.on_connect = robot_on_connect
    client.on_publish = robot_on_publish
    client.on_disconnect = robot_on_disconnect
    client.on_message = robot_on_message
    client.connect(mqtt_server, mqtt_port)
    client.loop_start()


def robot_on_connect(client, userdata, flags, rc):
    print("Client: {} MQTT return code: {}".format(
        client._client_id, mqtt_return[rc]))
    payload_str = "{}"
    payload_str_jso = json.loads(payload_str)
    payload_str_jso["connected"] = True
    payload_str = json.dumps(payload_str_jso)
    #client.publish(topicTelemetry, payload_str)
    client.subscribe(topicAttribute)


def robot_on_publish(client, userdata, mid):
    print("message is succesfully published")


def robot_on_message(client, userdata, msg):
    print("Message received: "+msg.topic+" "+msg.payload)
    handle_dummy_error(msg.payload)


def robot_on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection.")


def callback(data):
    # rospy.loginfo(data)
    # payload_str = "{}"
    # payload_str_jso = json.loads(payload_str)
    # payload_str_jso["polygon"] = "asd"
    # payload_str = json.dumps(payload_str_jso)
    client.publish(topicTelemetry, data.data)


if __name__ == "__main__":
    init_mqtt()
    time.sleep(2)
    try:
        init_node()
    except:
        print("Stopping the execution")
