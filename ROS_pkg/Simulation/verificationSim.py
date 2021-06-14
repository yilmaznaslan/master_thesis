import os
import sys
import time
import traci
import paho.mqtt.client as mqtt
import random
import json
import xml.etree.ElementTree as ET
import json
import numpy as np

# This script runs the sumo simulation defined in VerificationSim/cfg.sumocfg and creates randoim dusbtins GPS points along the paths
# IT should be called within the Simulation Directory


def create_dustbin_coor(route_path, n_dustbin):
    f = open(route_path, "r+")
    f_str = f.read()
    f.close()
    f_list = f_str.split(";")
    route_len = len(f_list)

    if(0):
        dustbin_list = []

        start = 0
        step = route_len//n_dustbin
        finish = start + step
        for i in range(1, n_dustbin+1):

            n1 = random.randint(start, finish)
            dustbin_list.append(n1)
            start = start + step
            finish = finish + step
        dustbin_list = sorted(dustbin_list)
    else:
        dustbin_array = np.linspace(5, route_len-5, n_dustbin)
        dustbin_array = dustbin_array.astype(np.int)
        dustbin_list = dustbin_array.tolist()

    dustbin_coor_path = route_path[:-4]+"_dustbin.txt"
    # print(dustbin_coor_path)
    f = open(dustbin_coor_path, "w+")
    for i in range(n_dustbin):
        rand_position = f_list[dustbin_list[i]]
        if i == 0:
            f.write(str(rand_position))
        else:
            f.write(";"+str(rand_position))
    f.close()
    print("{} dustbins succesfully created from route coordinates {}".format(n_dustbin, route_path))


def main():
    print("Working directory: "+os.getcwd())
    print("--------------- Simulation Verification started ----------------")
    routefile_path = "VerificationSim/simulation.rou.xml"
    routefile_doc = ET.parse(routefile_path)
    rname = "Robot1"
    root = routefile_doc.getroot()
    routes = routefile_doc.findall('route')
    vehicles = routefile_doc.findall('vehicle')
    for vehicle in vehicles:
        if(vehicle.get('id') == rname):
            vehicle.set('route', 'robot1_route1')
            routefile_str = ET.tostring(root, encoding='unicode')
            with open(routefile_path, "w") as f:
                f.write(routefile_str)
            print(rname + " route resetted to original")

    sumoBinary = "sumo"
    sumoCmd = [sumoBinary, "-c", "VerificationSim/cfg.sumocfg"]
    traci.start(sumoCmd)
    print("\nStarting SUMO")
    print("traci version:", traci.getVersion())

    path_rbt1_route = "VerificationSim/Coordinates/robot1_route.txt"
    path_rbt2_route = "VerificationSim/Coordinates/robot2_route.txt"
    path_mothership1_route = "VerificationSim/Coordinates/mothership1_route.txt"

    # Create Route Files
    f = open(path_rbt1_route, "w+")
    f.close()
    f = open(path_rbt2_route, "w+")
    f.close()
    f = open(path_mothership1_route, "w+")
    f.close()

    time.sleep(1)
    rbt1_index = 0
    rbt2_index = 0
    mothership1_index = 0

    rbt1_total_distance_traveled = 0
    rbt2_total_distance_traveled = 0

    while(1):
        traci.simulationStep()
        vehicles = traci.vehicle.getIDList()

        if("Robot1" in vehicles):
            x, y = traci.vehicle.getPosition("Robot1")
            lon, lat = traci.simulation.convertGeo(x, y)
            gps_position = [lat, lon]
            rbt1_total_distance_traveled = traci.vehicle.getDistance("Robot1")

            f = open("VerificationSim/Coordinates/robot1_route.txt", "a+")
            if(rbt1_index == 0):
                f.write(str(gps_position[0])+" "+str(gps_position[1]))
                rbt1_index += 1
            else:
                f.write(";"+str(gps_position[0])+" "+str(gps_position[1]))
            f.close()

        if("Robot2" in vehicles):
            x, y = traci.vehicle.getPosition("Robot2")
            lon, lat = traci.simulation.convertGeo(x, y)
            gps_position = [lat, lon]
            rbt2_total_distance_traveled = traci.vehicle.getDistance("Robot2")

            f = open("VerificationSim/Coordinates/robot2_route.txt", "a+")
            if(rbt2_index == 0):
                f.write(str(gps_position[0])+" "+str(gps_position[1]))
                rbt2_index += 1
            else:
                f.write(";"+str(gps_position[0])+" "+str(gps_position[1]))
            f.close()

        vehicle_name = "mothership1"
        if(vehicle_name in vehicles):
            x, y = traci.vehicle.getPosition(vehicle_name)
            lon, lat = traci.simulation.convertGeo(x, y)
            gps_position = [lat, lon]
            rbt2_total_distance_traveled = traci.vehicle.getDistance(vehicle_name)

            f = open("VerificationSim/Coordinates/"+vehicle_name + "_route.txt", "a+")
            if(mothership1_index == 0):
                f.write(str(gps_position[0])+" "+str(gps_position[1]))
                mothership1_index += 1
            else:
                f.write(";"+str(gps_position[0])+" "+str(gps_position[1]))
            f.close()

        if(not("Robot2" in vehicles) and not("Robot1" in vehicles) and not("mothership1" in vehicles)):
            print("\nEnd\n")
            break

    traci.close()
    print("End of SUMO Simulation")

    try:
        f = open("VerificationSim/summary.json", "w+")
        payload_str = "{}"
        payload_str_jso = json.loads(payload_str)
        payload_str_jso["Robot1"] = round(rbt1_total_distance_traveled)
        payload_str_jso["Robot2"] = round(rbt2_total_distance_traveled)
        payload_str = json.dumps(payload_str_jso)
        f.write(payload_str)
        f.close()
        print("Summary file succesfully created")
    except:
        print("Summary file couldnt be created")

    # Creating dustbins along the routes
    n_dustbin = 6
    create_dustbin_coor(path_rbt1_route, n_dustbin)
    create_dustbin_coor(path_rbt2_route, n_dustbin)

    print("--------------- Simulation Verification finished ----------------")


if __name__ == '__main__':
    main()
