#!/usr/bin/env python3

import rospy
import json
import time
import math
import threading
import random
from std_msgs.msg import String


payload_str = "{}"
payload_json = json.loads(payload_str)


pub_to_cloud = None

rbt1_coor = None
dustbin1_coor = None
dustbin1_coor_len = None
rbt1_coor_len = None
dummy_error = 0
rbt1_mode = "operating"

battery_init = 960  # Initial battery capacity, Wh
consumption_drive = 370  # W
consumption_empty = 128  # W
container_level = 0


def haversine(coord1, coord2):
    R = 6372800  # Earth radius in meters
    lat1, lon1 = coord1
    lat2, lon2 = coord2

    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi/2)**2 + \
        math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2

    return round((2*R*math.atan2(math.sqrt(a), math.sqrt(1 - a))), 2)


def get_dummy_error():
    global dummy_error
    return dummy_error


def set_dummy_error(val):
    global dummy_error
    dummy_error = val


def callback(data):
    if(data.data == "error_on"):
        set_dummy_error(1)
        payload_str = "{}"
        payload_json = json.loads(payload_str)
        payload_json["mode"] = "error"
        payload_str = json.dumps(payload_json)
        pub_to_cloud.publish(payload_str)

    if(data.data == "error_off"):
        set_dummy_error(0)
        payload_str = "{}"
        payload_json = json.loads(payload_str)
        payload_json["mode"] = "steering"
        payload_str = json.dumps(payload_json)
        pub_to_cloud.publish(payload_str)


def init_subscriber():
    rospy.Subscriber("veh_error", String, callback)
    print("ROS subscriber  is initialized")
    rospy.spin()


def init_node():
    global pub_to_cloud
    rospy.init_node('simulation', anonymous=True)
    pub_to_cloud = rospy.Publisher('cloud_message', String, queue_size=100)
    print("ROS Node is initialized")
    thread.start_new_thread(init_subscriber, ())


def init_route():
    global rbt1_coor, rbt1_coor_len, dustbin1_coor, dutsbin1_coor_len, payload_json
    # Open and read the task file for simulation
    f = open("/home/aslan/catkin_ws/src/murmel_comm/routes/task_simulation.json", "r+")
    task_str = f.read()
    f.close()
    task_json = json.loads(task_str)
    route_str = task_json["coordinates"]["route"].split(";")
    dustbin_str = task_json["coordinates"]["dustbin"].split(";")
    rbt1_coor_len = len(route_str)
    dustbin1_coor_len = len(dustbin_str)
    rbt1_coor = route_str
    dustbin1_coor = dustbin_str
    for i in range(rbt1_coor_len):
        rbt1_coor[i] = route_str[i].split(" ")
        rbt1_coor[i][1] = float(rbt1_coor[i][1])
        rbt1_coor[i][0] = float(rbt1_coor[i][0])

    for i in range(dustbin1_coor_len):
        dustbin1_coor[i] = dustbin_str[i].split(" ")
        dustbin1_coor[i][1] = float(dustbin1_coor[i][1])
        dustbin1_coor[i][0] = float(dustbin1_coor[i][0])
    print("Route details loaded")
    payload_json["total_distance"] = task_json["total_distance"]
    payload_json["vehType"] = "robot"
    payload_json["id"] = 1
    payload_json["routeid"] = 1
    payload_json["mode"] = "steering"
    payload_json["polygon"] = rbt1_coor
    payload_str = json.dumps(payload_json)
    pub_to_cloud.publish(payload_str)


def init_sim():
    global rbt1_mode, container_level, dustbin1_coor_len, state_pistion, state_container_lid, state_dustbin_lid, payload_json
    i = 1
    rate = rospy.Rate(1)
    distance_traveled = 0
    travel_time = 0
    dustbin_index = 0
    battery = battery_init

    while(not rospy.is_shutdown() and i < rbt1_coor_len):
        if(not get_dummy_error() == 1):
            # Publising GPS adn distance traveled coordinates
            distance = haversine(rbt1_coor[i], rbt1_coor[i-1])
            distance_traveled = distance_traveled+distance
            distanceToTarget = haversine(rbt1_coor[i], dustbin1_coor[dustbin_index])
            travel_time = distance  # Speed constant t = x/v
            energy_consumed = (travel_time/3600)*consumption_drive
            battery = battery - energy_consumed
            battery_level = round(battery/battery_init*100, 2)

            payload_json["latitude"] = rbt1_coor[i][0]
            payload_json["longitude"] = rbt1_coor[i][1]
            payload_json["distance_traveled"] = distance_traveled
            payload_json["distance_to_target"] = distanceToTarget
            payload_json["speed"] = 1
            payload_json["autopilot"] = 1
            payload_json["target"] = "Dustbin"+str(dustbin_index+1)
            payload_json["vehType"] = "robot"
            payload_json["vehid"] = 1
            payload_json["mode"] = "steering"
            payload_json["camera"] = 1
            payload_json["lidar"] = 1
            payload_json["proximity"] = 1
            payload_json["battery"] = battery_level
            payload_json["polygon"] = rbt1_coor
            #payload_json["targets_latitude"]
            

            if(distanceToTarget <= 1):

                payload_str = "{}"
                payload_json["mode"] = "operating"
                payload_json["speed"] = 0
                payload_json = json.loads(payload_str)
                battery = battery - (30.0/3600)*consumption_empty
                battery_level = round(battery/battery_init*100, 2)

                payload_json["container_lid"] = "opened"
                payload_json["battery"] = battery_level
                payload_str = json.dumps(payload_json)
                pub_to_cloud.publish(payload_str)
                time.sleep(4)
                battery = battery - (30.0/3600)*consumption_empty
                battery_level = round(battery/battery_init*100, 2)
                payload_json["dustbin_lid"] = "opened"
                payload_json["battery"] = battery_level
                payload_str = json.dumps(payload_json)
                pub_to_cloud.publish(payload_str)

                time.sleep(4)
                battery = battery - (30.0/3600)*consumption_empty
                battery_level = round(battery/battery_init*100, 2)
                payload_json["piston"] = "compressed"
                payload_json["battery"] = battery_level
                payload_str = json.dumps(payload_json)
                pub_to_cloud.publish(payload_str)
                time.sleep(4)

                battery = battery - (30.0/3600)*consumption_empty
                battery_level = round(battery/battery_init*100, 2)
                payload_json["dustbin_lid"] = "closed"
                payload_json["battery"] = battery_level
                payload_str = json.dumps(payload_json)
                pub_to_cloud.publish(payload_str)
                time.sleep(4)

                battery = battery - (30.0/3600)*consumption_empty
                battery_level = round(battery/battery_init*100, 2)
                payload_json["container_lid"] = "closed"
                payload_json["battery"] = battery_level
                payload_str = json.dumps(payload_json)
                pub_to_cloud.publish(payload_str)
                time.sleep(4)

                battery = battery - (30.0/3600)*consumption_empty
                battery_level = round(battery/battery_init*100, 2)
                payload_json["piston"] = "released"
                payload_json["battery"] = battery_level
                payload_str = json.dumps(payload_json)
                pub_to_cloud.publish(payload_str)

                container_level = container_level + random.randint(5, 15)
                payload_json["container"] = container_lev    def set_mqtt():el
                # print(container_level)
                payload_str = json.dumps(payload_json)
                pub_to_cloud.publish(payload_str)
                if(dustbin_index < 5):
                    dustbin_index = dustbin_index + 1

            payload_str = json.dumps(payload_json)
            pub_to_cloud.publish(payload_str)
            rate.sleep()
            i = i+1
    print("Simulation Ended")


if __name__ == "__main__":
    init_node()
    init_route()
    init_sim()
