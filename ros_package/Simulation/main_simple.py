
import webbrowser
import os
import sys
import time
import paho.mqtt.client as mqtt
import random
import json
import math
import numpy as np
import threading
import websocket
import ssl


ws_host = "wss://murmel.website:8000"
# Sensor initials
robot1_battery_init = 960  # Initial battery capacity, Wh
robot2_battery_init = 960  # Initial battery capacity, Wh
consumption_drive = 370  # W
consumption_empty = 128  # W

# Global MQTT variables
mqtt_server = 'demo.thingsboard.io'
#mqtt_server = 'localhost'
#mqtt_server = "ec2-35-165-45-85.us-west-2.compute.amazonaws.com"
mqtt_port = 1883
topicTelemetry = "v1/devices/me/telemetry"
topicAttribute = "v1/devices/me/attributes"
mqtt_return = {0: "Connection accepted",
               1: "Connection refused, unacceptable protocol version",
               2: "Connection refused, identifier rejected",
               3: "Connection refused, server unavailable",
               4: "Connection refused, bad user name or password",
               5: "Connection refused, not authorized"}
robot1_username = "Robot1_sim"
robot2_username = "Robot2_sim"
mothership1_username = "Mothership_sim"


# Global Route variables
robot1_route_coor = None
robot1_route2_coor = None
robot2_route_coor = None
mothership_route_coor = None
dustb1_coor = None
dustb2_coor = None
dustb1_coor_len = None
dustb2_coor_len = None

robot1_route1_total_distance = None
robot2_route1_total_distance = None

# Global robot modes
robot1_autopilot = 0
robot2_autopilot = 0

client_dustbins = [None]*12
client_robot1 = None
client_robot2 = None
client_mothership1 = None
random.seed(1)
rbt1_payload_str = "{}"
rbt1_payload_str_jso = json.loads(rbt1_payload_str)


rbt2_payload_str = "{}"
rbt2_payload_str_jso = json.loads(rbt2_payload_str)

robot1_coor_i = 0
robot2_coor_i = 0
robot1_dustbin_index = 0
robot2_dustbin_index = 0

robot1_container_level = 0
robot2_container_level = 0


def mqtt_on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection.")


def mqtt_on_publish(client, userdata, mid):
    pass


def mqtt_on_message(client, userdata, msg):
    global robot1_autopilot, robot2_autopilot
    msg_str = msg.payload.decode('utf-8')
    msg_json = json.loads(msg_str)
    client_id = client._client_id.decode('utf-8')
    # print(msg.payload)
    if(client_id == "Robot1_sim"):
        if(msg_json['autopilot'] != None):
            robot1_autopilot = msg_json['autopilot']
            print(client_id+" Autopilot:"+str(robot1_autopilot))
    if(client_id == "Robot2_sim"):
        if(msg_json['autopilot'] != None):
            robot2_autopilot = msg_json['autopilot']
            print(client_id + " Autopilot:" + str(robot2_autopilot))


def on_connect(client, userdata, flags, rc):
    global robot1_route_coor, robot2_route_coor
    global dustb1_coor, dustb2_coor
    global mqtt_server, mqtt_port, topicTelemetry, topicAttribute, mqtt_return
    global robot1_autopilot, robot2_autopilot
    global robot1_route1_total_distance, robot2_route1_total_distance
    global robot1_container_level, robot2_container_level
    cname = client._client_id.decode('utf-8')
    print("Client: {} MQTT return code: {}".format(cname, mqtt_return[rc]))
    client.subscribe(topicAttribute)
    payload_str = "{}"
    payload_json = json.loads(payload_str)
    if(client._client_id.decode('utf-8') == "Robot1_sim"):
        payload_json["coordinates"] = robot1_route_coor
        payload_json["autopilot"] = robot1_autopilot
        payload_json["vehid"] = 1
        payload_json["vehType"] = "robot"
        payload_json["mode"] = "steering"
        payload_json["total_distance"] = robot1_route1_total_distance
        payload_json["container"] = robot1_container_level
        payload_json["target"] = "Dustbin "+str(robot1_dustbin_index+1)
        client.subscribe(topicAttribute)

    if(client._client_id.decode('utf-8') == "Robot2_sim"):
        payload_json["coordinates"] = robot2_route_coor
        payload_json["autopilot"] = robot2_autopilot
        payload_json["vehType"] = "robot"
        payload_json["mode"] = "steering"
        payload_json["vehid"] = 2
        payload_json["total_distance"] = robot2_route1_total_distance
        payload_json["container"] = robot2_container_level
        payload_json["target"] = "Dustbin "+str(robot2_dustbin_index+7)
        client.subscribe(topicAttribute)

    if(cname.startswith("Dustbin")):
        i = int(cname[7:])
        if(i <= 6):
            payload_json["latitude"] = float(dustb1_coor[i-1][0])
            payload_json["longitude"] = float(dustb1_coor[i-1][1])
        else:
            payload_json["latitude"] = float(dustb2_coor[i-7][0])
            payload_json["longitude"] = float(dustb2_coor[i-7][1])
        payload_str = json.dumps(payload_json)
        client.publish(topicAttribute, payload_str)
        payload_str = "{}"
        payload_json = json.loads(payload_str)
        payload_json["full"] = 1

    payload_str = json.dumps(payload_json)
    client.publish(topicTelemetry, payload_str)


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


def init_route():
    # -----------------------  Import dustbins and Simulated Route coordinates ---------------------
    global robot1_route_coor, robot1_route2_coor, robot2_route_coor, dustb1_coor, dustb2_coor, mothership_route_coor
    global dustb1_coor_len, dustb2_coor_len
    global robot1_route1_total_distance, robot2_route1_total_distance
    f = open(
        "/home/aslan/catkin_ws/src/murmel_comm/Simulation/routes/route_simulation_rbt1.json", "r+")
    f_str = f.read()
    f.close()
    f_json = json.loads(f_str)
    robot1_route1_total_distance = f_json["total_distance"]
    robot1_route_str = f_json["coordinates"]["vehicle"].split(";")
    dustb1_route_str = f_json["coordinates"]["dustbin"].split(";")
    robot1_route_coor_len = len(robot1_route_str)
    dustb1_coor_len = len(dustb1_route_str)
    robot1_route_coor = robot1_route_str
    dustb1_coor = dustb1_route_str

    for i in range(robot1_route_coor_len):
        robot1_route_coor[i] = robot1_route_str[i].split(" ")
        robot1_route_coor[i][1] = float(robot1_route_coor[i][1])
        robot1_route_coor[i][0] = float(robot1_route_coor[i][0])
    for i in range(dustb1_coor_len):
        dustb1_coor[i] = dustb1_route_str[i].split(" ")
        dustb1_coor[i][1] = float(dustb1_coor[i][1])
        dustb1_coor[i][0] = float(dustb1_coor[i][0])

    f = open("/home/aslan/catkin_ws/src/murmel_comm/Simulation/routes/route_simulation_rbt1_updated.json", "r+")
    f_str = f.read()
    f.close()
    f_json = json.loads(f_str)
    robot1_route2_str = f_json["coordinates"]["vehicle"].split(";")
    robot1_route2_coor_len = len(robot1_route2_str)
    robot1_route2_coor = robot1_route2_str

    for i in range(robot1_route2_coor_len):
        robot1_route2_coor[i] = robot1_route2_str[i].split(" ")
        robot1_route2_coor[i][1] = float(robot1_route2_coor[i][1])
        robot1_route2_coor[i][0] = float(robot1_route2_coor[i][0])

    f = open(
        "/home/aslan/catkin_ws/src/murmel_comm/Simulation/routes/route_simulation_rbt2.json", "r+")
    f_str = f.read()
    f.close()
    f_json = json.loads(f_str)
    robot2_route1_total_distance = f_json["total_distance"]
    robot2_route_str = f_json["coordinates"]["vehicle"].split(";")
    dustb2_route_str = f_json["coordinates"]["dustbin"].split(";")
    robot2_route1_coor_len = len(robot2_route_str)
    dustb2_coor_len = len(dustb2_route_str)
    robot2_route_coor = robot2_route_str
    dustb2_coor = dustb2_route_str

    for i in range(robot2_route1_coor_len):
        robot2_route_coor[i] = robot2_route_str[i].split(" ")
        robot2_route_coor[i][1] = float(robot2_route_coor[i][1])
        robot2_route_coor[i][0] = float(robot2_route_coor[i][0])
    for i in range(dustb2_coor_len):
        dustb2_coor[i] = dustb2_route_str[i].split(" ")
        dustb2_coor[i][1] = float(dustb2_coor[i][1])
        dustb2_coor[i][0] = float(dustb2_coor[i][0])

    f = open(
        "/home/aslan/catkin_ws/src/murmel_comm/Simulation/routes/sim_mothership_route.json", "r+")
    f_str = f.read()
    f.close()
    f_json = json.loads(f_str)
    mothership_route_str = f_json["coordinates"]["vehicle"].split(";")
    mothership_coor_len = len(mothership_route_str)

    mothership_route_coor = mothership_route_str

    for i in range(mothership_coor_len):
        mothership_route_coor[i] = mothership_route_str[i].split(" ")
        mothership_route_coor[i][1] = float(mothership_route_coor[i][1])
        mothership_route_coor[i][0] = float(mothership_route_coor[i][0])


def init_mqtt():
    global mqtt_server, mqtt_port
    global robot1_username, robot2_username, mothership1_username, dustbin_username, client_dustbins
    global client_robot1, client_robot2, client_mothership1
    print("--------------- Connecting Robots to server ----------------")
    print(mqtt_server, mqtt_port, robot1_username)

    client_robot1 = mqtt.Client(robot1_username)
    client_robot1.username_pw_set(robot1_username)
    client_robot1.on_connect = on_connect
    client_robot1.on_publish = mqtt_on_publish
    client_robot1.on_disconnect = mqtt_on_disconnect
    client_robot1.on_message = mqtt_on_message
    client_robot1.connect(mqtt_server, mqtt_port)
    client_robot1.loop_start()

    client_robot2 = mqtt.Client(robot2_username)
    client_robot2.username_pw_set(robot2_username)
    client_robot2.on_connect = on_connect
    client_robot2.on_publish = mqtt_on_publish
    client_robot2.on_disconnect = mqtt_on_disconnect
    client_robot2.on_message = mqtt_on_message
    client_robot2.connect(mqtt_server, mqtt_port)
    client_robot2.loop_start()

    client_mothership1 = mqtt.Client(mothership1_username)
    client_mothership1.username_pw_set(mothership1_username)
    client_mothership1.on_connect = on_connect
    client_mothership1.connect(mqtt_server, mqtt_port)
    client_mothership1.loop_start()

    # client_dustbin = mqtt.Client(dustbin_username)
    # client_dustbin.username_pw_set(dustbin_username)
    # client_dustbin.on_connect = on_connect
    # client_dustbin.connect(mqtt_server, mqtt_port)
    # client_dustbin.loop_start()

    for i in range(0, 12):
        cname = "Dustbin"+str(i+1)
        client = mqtt.Client(cname)
        client.username_pw_set(cname)
        client.on_connect = on_connect
        client_dustbins[i] = client
        client_dustbins[i].connect(mqtt_server, mqtt_port)
        client_dustbins[i].loop_start()

    time.sleep(2)


def init_sim():
    global robot1_route_coor, robot1_route2_coor, robot2_route_coor, mothership_route_coor
    global mqtt_server, mqtt_port, topicTelemetry
    global client_robot1, client_robot2, client_mothership1
    global dustb1_coor, dustb2_coor
    global robot1_autopilot, robot2_autopilot
    payload_str = "{}"
    payload_json = json.loads(payload_str)
    print(len(robot2_route_coor), len(robot1_route_coor))
    robot1_coor_i = 0
    robot2_coor_i = 0
    mothership1_coor_i = 0
    robot1_dustbin_index = 0
    robot2_dustbin_index = 0
    print("starting to sim")
    distance_traveled = 0
    robot2_distance_traveled = 0

    while(1):

        if(robot1_coor_i < len(robot1_route_coor) and mothership1_coor_i > 30):
            payload_json["mode"] = "steering"
            distanceToTarget = haversine(
                robot1_route_coor[robot1_coor_i], dustb1_coor[robot1_dustbin_index])
            if(robot1_coor_i == 0 or not robot1_autopilot):
                distance = 0
            else:
                distance = haversine(
                    robot1_route_coor[robot1_coor_i], robot1_route_coor[robot1_coor_i-1])
                #distanceToTarget = haversine(robot1_route_coor[robot1_coor_i], dustb1_coor[robot1_dustbin_index])
            if(distanceToTarget <= 1):
                payload_str = "{}"
                payload_json["mode"] = "operating"
                payload_json["speed"] = 0
                payload_str = json.dumps(payload_json)
                client_robot1.publish(topicTelemetry, payload_str)

            distance_traveled = distance_traveled+distance

            # print(distance_traveled,distance)
            payload_str = "{}"
            payload_json = json.loads(payload_str)
            payload_json["autopilot"] = robot1_autopilot
            payload_json["latitude"] = float(
                robot1_route_coor[robot1_coor_i][0])
            payload_json["longitude"] = float(
                robot1_route_coor[robot1_coor_i][1])
            payload_json["distance_traveled"] = distance_traveled
            payload_json["distance_to_target"] = distanceToTarget

            payload_json["vehType"] = "robot"
            payload_json["vehid"] = 1

            payload_json["coordinates"] = robot1_route_coor

            payload_str = json.dumps(payload_json)
            client_robot1.publish(topicTelemetry, payload_str)
            if(robot1_autopilot):
                robot1_coor_i = robot1_coor_i + 1

        if(robot2_coor_i < len(robot2_route_coor) and mothership1_coor_i > 30):
            if(robot2_coor_i == 0 or not robot2_autopilot):
                distance = 0
            else:
                distance = haversine(
                    robot2_route_coor[robot2_coor_i], robot2_route_coor[robot2_coor_i-1])
            robot2_distance_traveled = robot2_distance_traveled+distance
            payload_str = "{}"
            payload_json = json.loads(payload_str)
            payload_json["autopilot"] = robot2_autopilot
            payload_json["latitude"] = float(
                robot2_route_coor[robot2_coor_i][0])
            payload_json["longitude"] = float(
                robot2_route_coor[robot2_coor_i][1])

            payload_json["distance_traveled"] = robot2_distance_traveled
            payload_json["vehType"] = "robot"
            payload_json["vehid"] = 2
            payload_json["mode"] = "steering"
            payload_json["coordinates"] = robot2_route_coor

            payload_str = json.dumps(payload_json)
            client_robot2.publish(topicTelemetry, payload_str)

            if(robot2_autopilot):
                robot2_coor_i = robot2_coor_i + 1

        payload_str = "{}"
        payload_json = json.loads(payload_str)
        payload_json["latitude"] = float(
            mothership_route_coor[mothership1_coor_i][0])
        payload_json["longitude"] = float(
            mothership_route_coor[mothership1_coor_i][1])
        payload_json["vehType"] = "mothership"
        payload_str = json.dumps(payload_json)
        client_mothership1.publish(topicTelemetry, payload_str)
        if(mothership1_coor_i < len(mothership_route_coor)-1):
            mothership1_coor_i += 1
            # print(mothership1_coor_i)

        if((robot1_coor_i == len(robot1_route_coor) and robot2_coor_i == len(robot2_route_coor))):
            print("End of the simulation")
            # print(robot1_coor_i,robot2_coor_i)
            break

        time.sleep(.2)


def ws_on_open(ws):
    print("Connected to the WebSocket Server at: "+ws_host)
    ws.send("robot1")


def ws_on_close(ws):
    print("### closed ###")


def ws_on_error(ws, error):
    print(error)


def ws_on_message(ws, msg):
    global robot1_coor_i
    global robot1_route_coor
    global robot1_route2_coor
    global robot1_dustbin_index
    if(msg == "route_update"):
        print("Route update request is received")
        print("Current GPS is: ", robot1_route_coor[robot1_coor_i])
        if(robot1_route_coor[robot1_coor_i] in robot1_route2_coor):
            print("asd")
            robot1_route_coor = robot1_route2_coor
            robot1_dustbin_index = 3


def init_ws():
    websocket.enableTrace(False)
    ws = websocket.WebSocketApp(ws_host, on_open=ws_on_open,
                                on_message=ws_on_message, on_error=ws_on_error, keep_running=False)
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
    # try:
    # result = ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})    # retrun trrue if error occurs

    # except:
    # print("aasds")


def sim_mothership():
    global mothership_route_coor
    global mqtt_server, mqtt_port, topicTelemetry
    global client_mothership1

    mothership1_coor_i = 0

    payload_str = "{}"
    payload_json = json.loads(payload_str)
    print("Starting to Mothership Simulation")

    while(1):
        payload_json["latitude"] = float(
            mothership_route_coor[mothership1_coor_i][0])
        payload_json["longitude"] = float(
            mothership_route_coor[mothership1_coor_i][1])
        payload_json["vehType"] = "mothership"
        payload_str = json.dumps(payload_json)
        client_mothership1.publish(topicTelemetry, payload_str)
        if(mothership1_coor_i == 30):
            print("Mothersip sim is finished")
            thread_robot1.start()
            thread_robot2.start()
            #break
        if(mothership1_coor_i < len(mothership_route_coor)-1):
            mothership1_coor_i += 1
        else:
            pass
        time.sleep(0.3)


def sim_robot1():
    print("starting to robot1 simulation")
    global robot1_route_coor
    global mqtt_server, mqtt_port, topicTelemetry
    global client_robot1, client_dustbins
    global dustb1_coor
    global robot1_autopilot
    global robot1_battery_init
    global robot1_coor_i
    global robot1_dustbin_index
    global robot1_container_level

    is_robot_finished = False
    container_level = robot1_container_level

    distance_traveled = 0
    battery = robot1_battery_init
    distanceToTarget = 0
    while(robot1_coor_i < len(robot1_route_coor)):
        payload_str = "{}"
        payload_json = json.loads(payload_str)

        if(robot1_autopilot):
            if(not is_robot_finished):
                distanceToTarget = haversine(
                    robot1_route_coor[robot1_coor_i], dustb1_coor[robot1_dustbin_index])
                payload_json["target"] = "Dustbin "+str(robot1_dustbin_index+1)
                payload_json["mode"] = "steering"
            else:
                distanceToTarget = haversine(
                    robot1_route_coor[robot1_coor_i], robot1_route_coor[-1])
                payload_json["target"] = "Mothership"
                payload_json["mode"] = "return"
            distance = haversine(
                robot1_route_coor[robot1_coor_i], robot1_route_coor[robot1_coor_i-1])
        else:
            distance = 0
        travel_time = distance  # Speed constant t = x/v
        energy_consumed = (travel_time/3600)*consumption_drive
        battery = battery - energy_consumed
        battery_level = round(battery/robot1_battery_init*100, 2)
        distance_traveled = distance_traveled+distance

        payload_json["latitude"] = float(robot1_route_coor[robot1_coor_i][0])
        payload_json["longitude"] = float(robot1_route_coor[robot1_coor_i][1])
        payload_json["coordinates"] = robot1_route_coor
        payload_json["vehType"] = "robot"
        payload_json["vehid"] = 1
        payload_json["speed"] = 1
        payload_json["camera"] = 1
        payload_json["lidar"] = 1
        payload_json["proximity"] = 1
        payload_json["autopilot"] = robot1_autopilot
        payload_json["distance_traveled"] = distance_traveled
        payload_json["distance_to_target"] = distanceToTarget
        payload_json["battery"] = battery_level

        if(distanceToTarget <= 1.5 and not is_robot_finished and robot1_autopilot):
            payload_str = "{}"
            payload_json["mode"] = "operating"
            payload_json["speed"] = 0

            payload_json["container_lid"] = "opened"
            payload_str = json.dumps(payload_json)
            client_robot1.publish(topicTelemetry, payload_str)
            time.sleep(1.5)

            payload_json["dustbin_lid"] = "opened"
            payload_str = json.dumps(payload_json)
            client_robot1.publish(topicTelemetry, payload_str)
            time.sleep(1.5)

            payload_json["piston"] = "compressed"
            payload_str = json.dumps(payload_json)
            client_robot1.publish(topicTelemetry, payload_str)
            time.sleep(1.5)

            payload_json["dustbin_lid"] = "closed"
            payload_str = json.dumps(payload_json)
            client_robot1.publish(topicTelemetry, payload_str)
            time.sleep(1.5)

            payload_json["container_lid"] = "closed"
            payload_str = json.dumps(payload_json)
            client_robot1.publish(topicTelemetry, payload_str)
            time.sleep(1.5)

            payload_json["piston"] = "released"
            container_level = container_level + random.randint(5, 15)
            payload_json["container"] = container_level
            payload_str = json.dumps(payload_json)
            client_robot1.publish(topicTelemetry, payload_str)
            time.sleep(1.5)

            payload_str = "{}"
            payload_json = json.loads(payload_str)
            payload_json["full"] = 0
            payload_str = json.dumps(payload_json)
            client_dustbins[robot1_dustbin_index].publish(
                topicTelemetry, payload_str)
            if(robot1_dustbin_index < 5):
                robot1_dustbin_index += 1
            else:
                is_robot_finished = True

        payload_str = json.dumps(payload_json)
        client_robot1.publish(topicTelemetry, payload_str)
        if(robot1_autopilot):
            robot1_coor_i += 1
        time.sleep(1.0)
    print("Robot1 simulations is ended")


def sim_robot2():
    print("starting to robot2 simulation")
    global robot2_route_coor
    global mqtt_server, mqtt_port, topicTelemetry
    global client_robot2, client_dustbins
    global dustb2_coor
    global robot2_autopilot
    global robot2_battery_init
    global robot2_coor_i
    global robot2_dustbin_index
    global robot2_container_level

    is_robot_finished = False
    container_level = robot1_container_level

    distance_traveled = 0
    battery = robot1_battery_init
    distanceToTarget = 0
    while(robot2_coor_i < len(robot2_route_coor)):
        payload_str = "{}"
        payload_json = json.loads(payload_str)

        if(robot2_autopilot):
            if(not is_robot_finished):
                distanceToTarget = haversine(
                    robot2_route_coor[robot2_coor_i], dustb2_coor[robot2_dustbin_index])
                payload_json["target"] = "Dustbin "+str(robot2_dustbin_index+7)
                payload_json["mode"] = "steering"
            else:
                distanceToTarget = haversine(
                    robot2_route_coor[robot2_coor_i], robot2_route_coor[-1])
                payload_json["target"] = "Mothership"
                payload_json["mode"] = "return"
            distance = haversine(
                robot2_route_coor[robot2_coor_i], robot2_route_coor[robot2_coor_i-1])
        else:
            distance = 0
        travel_time = distance  # Speed constant t = x/v
        energy_consumed = (travel_time/3600)*consumption_drive
        battery = battery - energy_consumed
        battery_level = round(battery/robot2_battery_init*100, 2)
        distance_traveled = distance_traveled+distance

        payload_json["latitude"] = float(robot2_route_coor[robot2_coor_i][0])
        payload_json["longitude"] = float(robot2_route_coor[robot2_coor_i][1])
        payload_json["coordinates"] = robot2_route_coor
        payload_json["vehType"] = "robot"
        payload_json["vehid"] = 2
        payload_json["speed"] = 1
        payload_json["camera"] = 1
        payload_json["lidar"] = 1
        payload_json["proximity"] = 1
        payload_json["autopilot"] = robot2_autopilot
        payload_json["distance_traveled"] = distance_traveled
        payload_json["distance_to_target"] = distanceToTarget
        payload_json["battery"] = battery_level

        if(distanceToTarget <= 1.5 and not is_robot_finished and robot2_autopilot):
            payload_str = "{}"
            payload_json["mode"] = "operating"
            payload_json["speed"] = 0

            payload_json["container_lid"] = "opened"
            payload_str = json.dumps(payload_json)
            client_robot2.publish(topicTelemetry, payload_str)
            time.sleep(1.5)

            payload_json["dustbin_lid"] = "opened"
            payload_str = json.dumps(payload_json)
            client_robot2.publish(topicTelemetry, payload_str)
            time.sleep(1.5)

            payload_json["piston"] = "compressed"
            payload_str = json.dumps(payload_json)
            client_robot2.publish(topicTelemetry, payload_str)
            time.sleep(1.5)

            payload_json["dustbin_lid"] = "closed"
            payload_str = json.dumps(payload_json)
            client_robot2.publish(topicTelemetry, payload_str)
            time.sleep(1.5)

            payload_json["container_lid"] = "closed"
            payload_str = json.dumps(payload_json)
            client_robot2.publish(topicTelemetry, payload_str)
            time.sleep(1.5)

            payload_json["piston"] = "released"
            container_level = container_level + random.randint(5, 15)
            payload_json["container"] = container_level
            payload_str = json.dumps(payload_json)
            client_robot2.publish(topicTelemetry, payload_str)
            time.sleep(0.5)

            payload_str = "{}"
            payload_json = json.loads(payload_str)
            payload_json["full"] = 0
            payload_str = json.dumps(payload_json)
            client_dustbins[robot2_dustbin_index +
                            6].publish(topicTelemetry, payload_str)
            if(robot2_dustbin_index < 5):
                robot2_dustbin_index += 1
            else:
                is_robot_finished = True

        payload_str = json.dumps(payload_json)
        client_robot2.publish(topicTelemetry, payload_str)
        if(robot2_autopilot):
            robot2_coor_i += 1
        time.sleep(1.0)
    print("Robot2 simulations is ended")


def keep_alive():
    while(1):
        # print("bale")
        time.sleep(1)
        try:
            pass
        except KeyboardInterrupt:
            print("\nGot it")


if __name__ == "__main__":
    init_route()
    init_mqtt()
    thread_ws = threading.Thread(target=init_ws, args=())
    thread_ws.start()
    thread_robot1 = threading.Thread(target=sim_robot1, args=())
    thread_robot2 = threading.Thread(target=sim_robot2, args=())
    thread_mothership = threading.Thread(target=sim_mothership, args=())
    thread_mothership.start()
    thread_alive = threading.Thread(target=keep_alive, args=())
    thread_alive.start()
