#!/usr/bin/env python

from std_msgs.msg import String
from cv_bridge import CvBridge, CvBridgeError
from sensor_msgs.msg import Image
import rospy
import base64
import websocket
try:
    import thread
except ImportError:
    import _thread as thread
import time
import numpy as np
import cv2
import pickle
from sys import getsizeof
from cv_bridge import CvBridge
import os
import ssl
bridge = CvBridge()
ws_host = "murmel.website"
ws_port = "8000"

frame = np.ones((480, 640, 3), dtype=np.uint8)


def set_frame(frame_in):
    global frame
    frame = frame_in


def callback(data):
    #rospy.loginfo(rospy.get_caller_id() + "I heard %s", data.data)
    #rospy.loginfo("Got img")
    cv_image = bridge.imgmsg_to_cv2(data, desired_encoding="passthrough")
    set_frame(cv_image)


def listener():
    rospy.Subscriber("rgb_frame", Image, callback)
    print("ROS Subcriber initialized")
    rospy.spin()


def get_frame():
    global frame
    return frame


def on_message(ws, msg):
    if(msg == "start"):
        frame = get_frame()
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 65]
        frame_enc = cv2.imencode('.jpg', frame)[1]
        ws.send(frame_enc.tobytes(), opcode=0x02)  # Sending byte stream
    if(msg.startswith("route")):
        route = msg[5:]
        print("Route received")
        path = "/home/aslan/catkin_ws/src/murmel_comm/routes"
        f = open(path+"/robot1_route.txt", "w+")
        f.write(route)
        f.close()


def on_error(ws, error):
    print(error)


def on_close(ws):
    print("### closed ###")


def on_open(ws):
    print("Connected to Server")
    ws.send("robot1")


def init_node():
    print("Path at terminal"+os.getcwd() + "\n")
    rospy.init_node('connection_websocket', anonymous=True)
    print("ROS Node initialized")


def init_frame_susbcriber_thread():
    thread.start_new_thread(listener, ())


if __name__ == "__main__":
    init_node()
    init_frame_susbcriber_thread()
    websocket.enableTrace(False)
    ws = websocket.WebSocketApp("wss://"+ws_host+":8000", on_open=on_open,
                                on_message=on_message, on_error=on_error, keep_running=False)
    try:
        result = ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})    # retrun trrue if error occurs
    except:
        print("aasds")
    print(result)
    # for i in range(2):
    #     print("Trying to reconnect")

    #     result = ws.run_forever()
    #     print(result)
    #     time.sleep(1)
    # print("Connections failed")

