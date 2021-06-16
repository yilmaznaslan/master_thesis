import webbrowser
import os
import sys
import time
import traci
import paho.mqtt.client as mqtt
import random
import json
import math
import numpy as np
from xml.dom import minidom
random.seed(1)
import xml.etree.ElementTree as ET
import verificationSim
rbt1_payload_str = "{}"
rbt1_payload_str_jso = json.loads(rbt1_payload_str)


rbt2_payload_str = "{}"
rbt2_payload_str_jso = json.loads(rbt2_payload_str)




# -------------------------------- Runing the verficationSim.py ----------------------------------

# By importing the verficiationSim a pre Sumo Simulations is run to provision coordinates of vehicles and dustbins in advance
# If is there any error here, it should be handled in advance

 # -------------------------------- Initialize the Page ----------------------------------
#print("Dashboard is opening in the browser")
#dashboardlink = "https://demo.thingsboard.io/dashboard/def93110-3244-11eb-a402-b3c3ed579b6e?publicId=f8c07f10-71d1-11ea-8e0a-7d0ef2a682d3"
##webbrowser.open(dashboardlink, new=1)
#print("Simulation will start in 10 seconds")
#for i in range(10, 0, -1):
    #time.sleep(1)
    #print(i)
# -------------------------------- MQTT SERVER Creditentials----------------------------------
#mqtt_server = '192.168.178.21'
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
robot1_username = "Robot1"
robot2_username = "Robot2"
mothership1_username = "Mothership1"
# -----------------------  Import dustbins and Simulated Route coordinates ---------------------
f = open("VerificationSim/Coordinates/robot1_route_dustbin.txt", "r+")
f_str = f.read()
f.close()
f_strNe = f_str.split(";")
rbt1_dstbn_coor = f_strNe
for i in range(len(f_strNe)):
    rbt1_dstbn_coor[i] = f_strNe[i].split(" ")
    rbt1_dstbn_coor[i][1] = float(rbt1_dstbn_coor[i][1])
    rbt1_dstbn_coor[i][0] = float(rbt1_dstbn_coor[i][0])

f = open("VerificationSim/Coordinates/robot2_route_dustbin.txt", "r+")
f_str = f.read()
f.close()
f_strNe = f_str.split(";")
rbt2_dstbn_coor = f_strNe
for i in range(len(f_strNe)):
    rbt2_dstbn_coor[i] = f_strNe[i].split(" ")
    rbt2_dstbn_coor[i][1] = float(rbt2_dstbn_coor[i][1])
    rbt2_dstbn_coor[i][0] = float(rbt2_dstbn_coor[i][0])

# -----------------------  Import Simulated Route coordinates ---------------------

f = open("VerificationSim/Coordinates/robot1_route.txt", "r+")
f_str = f.read()
f.close()
f_strNe = f_str.split(";")
rbt1_coor = f_strNe
for i in range(len(f_strNe)):
    rbt1_coor[i] = f_strNe[i].split(" ")
    rbt1_coor[i][1] = float(rbt1_coor[i][1])
    rbt1_coor[i][0] = float(rbt1_coor[i][0])

f = open("VerificationSim/Coordinates/robot2_route.txt", "r+")
f_str = f.read()
f.close()
f_strNe = f_str.split(";")
rbt2_coor = f_strNe
for i in range(len(f_strNe)):
    rbt2_coor[i] = f_strNe[i].split(" ")
    rbt2_coor[i][1] = float(rbt2_coor[i][1])
    rbt2_coor[i][0] = float(rbt2_coor[i][0])



# ------------------------------- CallBack Functions ------------------------------


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


def robot_on_connect(client, userdata, flags, rc):
    print("Client: {} MQTT return code: {}".format(
        client._client_id, mqtt_return[rc]))
    payload_str = "{}"
    payload_str_jso = json.loads(payload_str)
    if(str(client._client_id) == "b\'Robot1\'"):
        f = open("VerificationSim/Coordinates/robot1_route.txt", "r+")
        f_str = f.read()
        f.close()
        f_strNe = f_str.split(";")
        rbt11_coor = f_strNe
        for i in range(len(f_strNe)):
            rbt1_coor[i] = f_strNe[i].split(" ")
            rbt1_coor[i][1] = float(rbt1_coor[i][1])
            rbt1_coor[i][0] = float(rbt1_coor[i][0])
        payload_str_jso["polygon"] = rbt1_coor
        payload_str_jso["id"] = 1
        payload_str = json.dumps(payload_str_jso)
        client.publish(topicTelemetry, payload_str)
        rbt1_payload_str_jso["autopilot"] = 0

    if(str(client._client_id) == "b\'Robot2\'"):
        payload_str_jso["polygon"] = rbt2_coor
        payload_str_jso["id"] = 2
        payload_str = json.dumps(payload_str_jso)
        client.publish(topicTelemetry, payload_str)
        rbt2_payload_str_jso["autopilot"] = 0
    client.subscribe(topicAttribute)
    client.publish(topicAttribute,"{\"autopilot\":0}")

def robot_on_message(client, userdata, msg):
    msg_str = str(msg.payload)[2:-1]
    msg_str_jso = json.loads(msg_str)
    rname = str(client._client_id)[2:-1]
    keys = msg_str_jso.keys()
    print(rname+ " recevied message" + msg_str)
    if(rname == "Robot1"):  
        if("routeupdate" in keys):
            routefile_path = "VerificationSim/simulation.rou.xml"
            routefile_doc = ET.parse(routefile_path)
            root = routefile_doc.getroot()
            routes = routefile_doc.findall('route')
            vehicles = routefile_doc.findall('vehicle')
            for route in routes:
                if(route.get('id') == 'robot1_route2'):               
                    for vehicle in vehicles:
                        if(vehicle.get('id')== rname):
                            vehicle.set('route','robot1_route2')
                            routefile_str = ET.tostring(root,encoding='unicode')
                            try:
                                traci.vehicle.setRouteID(rname,'robot1_route2')
                                with open(routefile_path, "w") as f: 
                                    f.write(routefile_str)          
                                f = open("VerificationSim/Coordinates/robot1_route_updated.txt", "r+")
                                f_str = f.read()
                                f.close()
                                f_strNe = f_str.split(";")
                                rbt1_coor = f_strNe
                                for i in range(len(f_strNe)):
                                    rbt1_coor[i] = f_strNe[i].split(" ")
                                    rbt1_coor[i][1] = float(rbt1_coor[i][1])
                                    rbt1_coor[i][0] = float(rbt1_coor[i][0])
                                payload_str = "{}"
                                payload_str_jso = json.loads(payload_str)
                                payload_str_jso["polygon"] = rbt1_coor
                                payload_str = json.dumps(payload_str_jso)
                                client.publish(topicTelemetry, payload_str)
                                print(rname + " Route succesfully updated")
                                rbt1_payload_str_jso['route_update'] = 1
                            except:
                                print(rname + " Route Update failed")
                                rbt1_payload_str_jso['route_update'] = 0



        if("autopilot" in keys):        
            if(msg_str_jso["autopilot"] == 0):
                print(rname," Autopilot mode deactivated Vehicle Stopped")
                rbt1_payload_str_jso["autopilot"] = 0
            if(msg_str_jso["autopilot"] == 1):
                print(rname," Autopilot mode activated Vehicle moves")
                rbt1_payload_str_jso["autopilot"] = 1
                traci.vehicle.setSpeed(rname,1)

    if(rname == "Robot2"):  
        if("autopilot" in keys):        
            if(msg_str_jso["autopilot"] == 0):
                print(rname," Autopilot mode deactivated Vehicle Stopped")
                rbt2_payload_str_jso["autopilot"] = 0
            if(msg_str_jso["autopilot"] == 1):
                print(rname," Autopilot mode activated Vehicle moves")
                rbt2_payload_str_jso["autopilot"] = 1
                traci.vehicle.setSpeed(rname,1)

def robot_on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection.")

def robot_on_publish(client, userdata, mid):
    a = 5

def dust_on_connect(client, userdata, flags, rc):
    global dustbin_index
    print("Client: {} MQTT return code: {}".format(
        client._client_id, mqtt_return[rc]))
    payload_str = "{}"
    payload_str_jso = json.loads(payload_str)
    # print(dustbin_index)
    if(dustbin_index < 6):
        payload_str_jso["latitude"] = rbt1_dstbn_coor[dustbin_index][0]
        payload_str_jso["longitude"] = rbt1_dstbn_coor[dustbin_index][1]
        payload_str_jso["id"] = 1
        payload_str_jso["polygon"] = rbt1_coor
    else:
        payload_str_jso["latitude"] = rbt2_dstbn_coor[dustbin_index-6][0]
        payload_str_jso["longitude"] = rbt2_dstbn_coor[dustbin_index-6][1]
        payload_str_jso["id"] = 2
        payload_str_jso["polygon"] = rbt2_coor
    payload_str = json.dumps(payload_str_jso)
    client.publish(topicAttribute, payload_str)
    payload_str = "{}"
    payload_str_jso = json.loads(payload_str)
    payload_str_jso["full"] = 1
    payload_str = json.dumps(payload_str_jso)
    client.publish(topicTelemetry, payload_str)
    dustbin_index += 1


def dust_on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))


def dust_on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection.")


def dust_on_publish(client, userdata, mid):
    print("Mid: {} Publish SUCCESFULL".format(mid))


# ------------------------------ Establish Robot Connections ----------------------
print("--------------- Connecting Robots to server ----------------")
robots_username = "Robots"
robots_clients = []
nrobots = 2
for i in range(nrobots):
    cname = "Robot"+str(i+1)
    client = mqtt.Client(cname)
    #print("Client {} created".format(cname))
    client.username_pw_set(cname)
    client.on_connect = robot_on_connect
    client.on_publish = robot_on_publish
    client.on_disconnect = robot_on_disconnect
    client.on_message = robot_on_message
    robots_clients.append(client)
    client.connect(mqtt_server, mqtt_port)
    client.loop_start()
    time.sleep(1)


# ------------------------------ Establish Dustbin connections -----------------------------
print("--------------- Connecting Dustbins to server ----------------")
dustbin_index = 0
dustbin_username = "Dustbin"
dustbin_clients = []
for i in range(12):
    cname = "Dustbin"+str(i+1)
    client = mqtt.Client(cname)
    dustbin_clients.append(client)
    #print("Client {} created".format(cname))
    client.username_pw_set(cname)
    client.on_connect = dust_on_connect
    #client.on_publish = dust_on_publish
    client.on_disconnect = dust_on_disconnect
    client.on_message = dust_on_message
    client.connect(mqtt_server, mqtt_port)
    client.loop_start()
    time.sleep(0.5)

# ------------------------------ Establish Mothership Connections ----------------------
print("--------------- Connecting Mothership to server ----------------")
mothership1_client = mqtt.Client()
mothership1_client.username_pw_set(mothership1_username)
mothership1_client.on_connect = robot_on_connect
mothership1_client.on_publish = robot_on_publish
mothership1_client.on_disconnect = robot_on_disconnect
mothership1_client.on_message = robot_on_message
mothership1_client.connect(mqtt_server, mqtt_port)
mothership1_client.loop_start()
print("--------------- Connectins are established  ----------------")
# ------------------------------------- Starting SUMO Simulation -------------------------------------
time.sleep(2)
sumoBinary = "sumo-gui"
sumoCmd = [sumoBinary, "-c", "VerificationSim/cfg.sumocfg"]
traci.start(sumoCmd)
print("Traci version: " +str(traci.getVersion()))
print("--------------- Sumo is starting  ----------------")

# --------------------------- Variables used ----------------------
rbt1_dstbn_i = 0
rbt2_dstbn_i = 0

step_time = 0.5

rbt1_timer = 0
rbt2_timer = 0


rbt1_isFinished = False
rbt2_isFinished = False

rbt1_container = 0
rbt2_container = 0

rbt1_battery = 100
rbt2_battery = 100

rbt1_payload_str_jso["mode"] = "steering"
rbt2_payload_str_jso["mode"] = "steering"
# --------------------------- Setting up the simulation speed ----------------------
sim_mode = "slow"

if sim_mode =="slow":
    step_time = 0.3
    operation_duration  = 90*step_time

if sim_mode =="fast":
    step_time = 0.1
    operation_duration  = 300*step_time
simstep = 0

while(1):
    simstep = simstep +1
    time.sleep(step_time)
    traci.simulationStep()
    vehicles = traci.vehicle.getIDList()

    # Sending Telemetry data from robot1
    rname = "Robot1"
    if (rname in vehicles and (not rbt1_isFinished)):
        x, y = traci.vehicle.getPosition(rname)
        lon, lat = traci.simulation.convertGeo(x, y)
        speed = traci.vehicle.getSpeed(rname)
        position = [lat, lon]
        target_id = str(dustbin_clients[rbt1_dstbn_i]._client_id)
        target_pos = rbt1_dstbn_coor[rbt1_dstbn_i]
        distanceToTarget = haversine(target_pos, [lat, lon])
        routeid = traci.vehicle.getRouteID(rname)
        total_distance_traveled = traci.vehicle.getDistance(rname)

        # Autopilot disabled
        if(rbt1_payload_str_jso["autopilot"] == 0):
            traci.vehicle.setSpeed(rname,0)
            #print("routeID",traci.vehicle.getRoute(rname))
            #if( simstep == 100):
            #traci.vehicle.setRouteID(rname,"robot1_route2")
       
        # Autopilot enabled
        if(rbt1_payload_str_jso["autopilot"] == 1):

            if(rbt1_payload_str_jso["mode"] == "steering"):
                print("{} is steering  to target: {}. Distance to Target is: {} mt".format(rname, target_id, distanceToTarget))
                rbt1_battery = round((rbt1_battery - random.uniform(0.05,0.25)),2)
                if(distanceToTarget <= 1):
                    print("{} is arrived   to target: {}".format(rname, target_id))
                    traci.vehicle.setSpeed(rname, 0)
                    rbt1_payload_str_jso["mode"] = "operating"

            if(rbt1_payload_str_jso["mode"] == "operating"):
                print("{} is operating on target: {}".format(rname, target_id))
                rbt1_battery = round((rbt1_battery - random.uniform(0.05,0.25)),2)
                rbt1_timer += 1
                if(rbt1_timer >= operation_duration):
                    rbt1_payload_str_jso["mode"] = "steering"
                    rbt1_payload_strr = "{}"
                    rbt1_container = rbt1_container + random.randint(15, 20)               
                    rbt1_payload_strr_jso = json.loads(rbt1_payload_strr)
                    rbt1_payload_strr_jso["full"] = 0
                    rbt1_payload_strr = json.dumps(rbt1_payload_strr_jso)
                    dustbin_clients[rbt1_dstbn_i].publish(topicTelemetry, rbt1_payload_strr)
                    traci.vehicle.setSpeed(rname, 1)
                    if(rbt1_dstbn_i == (len(rbt1_dstbn_coor)-1)):
                        print("{}'mission is completed heading to Mothership".format(rname))
                        rbt1_payload_str_jso["mode"] = "return"
                        rbt1_isFinished = True
                    else:
                        print("{} is finished operating heading to next target".format(rname))
                        rbt1_dstbn_i += 1
                        rbt1_timer = 0
                        
        
        rbt1_payload_str_jso["id"] = 1
        rbt1_payload_str_jso["distance_traveled"] = total_distance_traveled
        rbt1_payload_str_jso["routeid"] = routeid
        rbt1_payload_str_jso["speed"] = speed
        rbt1_payload_str_jso["target"] = target_id
        rbt1_payload_str_jso["distance"] = distanceToTarget
        rbt1_payload_str_jso["latitude"] = lat
        rbt1_payload_str_jso["longitude"] = lon
        rbt1_payload_str_jso["vehType"] = "robot"
        rbt1_payload_str_jso["polygon"] = rbt1_coor
        rbt1_payload_str_jso["battery"] = rbt1_battery
        #rbt1_payload_str_jso["container"] = rbt1_container
        rbt1_payload_str_jso["camera"] = 1
        rbt1_payload_str_jso["lidar"] = 1
        rbt1_payload_str_jso["proximity"] = 1
        rbt1_payload_str = json.dumps(rbt1_payload_str_jso)
        robots_clients[0].publish(topicTelemetry, rbt1_payload_str)



    # Sending Telemetry data from robot1
    rname = "Robot2"
    if (rname in vehicles and (not rbt2_isFinished)):
        x, y = traci.vehicle.getPosition(rname)
        lon, lat = traci.simulation.convertGeo(x, y)
        speed = traci.vehicle.getSpeed(rname)
        position = [lat, lon]
        target_id = str(dustbin_clients[rbt2_dstbn_i+6]._client_id)
        target_pos = rbt2_dstbn_coor[rbt2_dstbn_i]
        distanceToTarget = haversine(target_pos, [lat, lon])
        routeid = traci.vehicle.getRouteID(rname)
        total_distance_traveled = traci.vehicle.getDistance(rname)

        # Autopilot disabled
        if(rbt2_payload_str_jso["autopilot"] == 0):
            traci.vehicle.setSpeed(rname,0)

        # Autopilot enabled
        if(rbt2_payload_str_jso["autopilot"] == 1):
            if(rbt2_payload_str_jso["mode"] == "steering"):          
                print("{} is steering  to target: {}. Distance to Target is: {} mt".format(rname, target_id, distanceToTarget))
                rbt2_battery = round((rbt2_battery - random.uniform(0.05,0.25)),2)
                if(distanceToTarget <= 1):
                    print("{} is arrived   to target: {}".format(rname, target_id))
                    traci.vehicle.setSpeed(rname, 0)
                    rbt2_payload_str_jso["mode"] = "operating"

            if(rbt2_payload_str_jso["mode"]=="operating"):
                print("{} is operating on target: {}".format(rname, target_id))
                rbt2_battery = round((rbt2_battery - random.uniform(0.05,0.25)),2)
                rbt2_timer += 1
                if(rbt2_timer >= operation_duration):
                    rbt2_payload_str_jso["mode"] = "steering"
                    rbt2_payload_strr = "{}"
                    rbt2_container = rbt2_container + random.randint(15, 20)               
                    rbt2_payload_strr_jso = json.loads(rbt2_payload_strr)
                    rbt2_payload_strr_jso["full"] = 0
                    rbt2_payload_strr = json.dumps(rbt2_payload_strr_jso)
                    dustbin_clients[rbt2_dstbn_i+6].publish(topicTelemetry, rbt2_payload_strr)
                    traci.vehicle.setSpeed(rname, 1)
                    if(rbt2_dstbn_i == (len(rbt2_dstbn_coor)-1)):
                        print("{}'mission is completed heading to Mothership".format(rname))
                        rbt2_payload_str_jso["mode"] = "return"
                        rbt2_isFinished = True
                    else:
                        print("{} is finished operating heading to next target".format(rname))
                        rbt2_dstbn_i += 1
                        rbt2_timer = 0
                        
        rbt2_payload_str_jso["id"] = 2
        rbt2_payload_str_jso["distance_traveled"] = total_distance_traveled
        rbt1_payload_str_jso["routeid"] = routeid
        rbt2_payload_str_jso["speed"] = speed
        rbt2_payload_str_jso["target"] = target_id
        rbt2_payload_str_jso["distance"] = distanceToTarget
        rbt2_payload_str_jso["latitude"] = lat
        rbt2_payload_str_jso["longitude"] = lon
        rbt2_payload_str_jso["vehType"] = "robot"
        rbt2_payload_str_jso["polygon"] = rbt2_coor
        rbt2_payload_str_jso["battery"] = rbt2_battery
        rbt2_payload_str_jso["container"] = rbt2_container
        rbt2_payload_str_jso["camera"] = 1
        rbt2_payload_str_jso["lidar"] = 1
        rbt2_payload_str_jso["proximity"] = 1
        rbt2_payload_str_jso["dustbin_lid"] = "closed"
        rbt2_payload_str_jso["container_lid"] = "closed"
        rbt2_payload_str_jso["piston"] = "compressed"
        rbt2_payload_str_jso["total_distance"] = 524
        rbt2_payload_str = json.dumps(rbt2_payload_str_jso)
        robots_clients[1].publish(topicTelemetry, rbt2_payload_str)





    # Sending Telemetry data from mothership
    rname = "mothership1"
    if (rname in vehicles):
        payload_str = "{}"
        payload_str_jso = json.loads(payload_str)
        x, y = traci.vehicle.getPosition("mothership1")
        lon, lat = traci.simulation.convertGeo(x, y)
        payload_str_jso["speed"] = traci.vehicle.getSpeed("mothership1")
        payload_str_jso["latitude"] = lat
        payload_str_jso["longitude"] = lon
        payload_str_jso["vehType"] = "mothership"
        #print("{} Electrcy consumption: ".format(rname,traci.vehicle.getElectricityConsumption(rname)))
        payload_str = json.dumps(payload_str_jso)
        mothership1_client.publish(topicTelemetry, payload_str)

print("Simulation Ended")
traci.close(sumoCmd)