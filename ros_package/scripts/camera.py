#!/usr/bin/env python

import rospy
import cv2
import sys
import numpy as np
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError 
import time

pub  = None
rate =  None
bridge = CvBridge()
resource = 2  # 2 for external camera
def init_camera():
  
    cap = cv2.VideoCapture(resource)
    if not cap.isOpened():
        print("Error opening resource: " + str(resource))
        exit(0)

    print("Correctly opened resource, starting to show feed.")
    ret, frame = cap.read()
    print(type(frame))
    cv2.imwrite("asd.jpeg",frame)
    if(not ret):
        print("Couldnt read the frame")
        exit()
    global pub
    while not rospy.is_shutdown():
        ret, frame = cap.read()     
        frame = frame.reshape((480,640,3))
        frame = frame.astype(np.uint8)

        ros_image = bridge.cv2_to_imgmsg(frame, encoding="passthrough")
        #rospy.loginfo("Streaming")
        pub.publish(ros_image)  
        rate.sleep()

def init_node():
    global pub,rate
    rospy.init_node('image_publisher', anonymous=True)
    pub = rospy.Publisher('rgb_frame', Image, queue_size=100)
    if pub != None:
        print("pub created")
    rate = rospy.Rate(30) # not sure this is necessary


if __name__ == '__main__':
    init_node()
    try:
        init_camera()
    except:
        print("\end")
    

 
    