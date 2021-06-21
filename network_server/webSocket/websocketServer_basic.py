"""
This script is used to handle the camera streaming from a robot and route file upload to a robot.
Since the project has currently only one single robot, script is designed to support a single robot.
"""
import asyncio
import websockets
import cv2
import numpy as np
import random
import pickle
import ssl
import os
import socket
from datetime import datetime


class robot_camera_client():
    count = 0

    def __init__(self):
        robot_camera_client.count += 1

    def __del__(self):
        class_name = self.__class__.__name__
        #print(class_name, " destroyed")
        robot_camera_client.count -= 1
        print(datetime.now().strftime("%c") +f" Current active {class_name} count is {robot_camera_client.count}")


class robot:
    """
    Robot class is used to handle each robot object. Although in the current state of the project there is only one robot,
    for simulating purposes or in a future scenerio with multiple robots, robot objects will be useful
    """
    count = 0
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 65]

    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.is_alive = False
        self.stream_mode = False
        self.frame = np.ones((640, 480, 3))*150
        robot.count = robot.count + 1

    def get_total_count(self):
        print(robot.count)

    def set_frame(self, frame):
        self.frame = frame

    def get_frame(self):
        return cv2.imencode('.jpg', self.frame, robot.encode_param)[1]


websocket_robot1 = None


def init_host():
    """ 
    Replace IP address with the public IP address or host name of the server machine
    """

    # Creating global variables
    global ws_host_port, ws_host_ip, ws_host_name

    ws_host_name = socket.gethostname()
    ws_host_ip = socket.gethostbyname(ws_host_name)
    ws_host_port = 8000

    print(f"Starting the WebSocket Server at\nName:\t{ws_host_name}\nIP:\t{ws_host_ip}\nPort:\t{ws_host_port}")


def init_robot_instances():
    """
    Initiates a robot object to handle the Robot 
    """
    global robot1
    robot1 = robot(1, "robot1_real")


def set_context():
    """
    Context settings in case SSL encryption is needed. Please make sure to use correct private key for server.
    """

    global context
    path = os.environ['murmel_application_server']
    print('path to env variable'+os.environ['murmel_application_server'])
    context = ssl.SSLContext()
    context.load_cert_chain(path+'/certificates/cert.crt', path+'/certificates/private.key')


async def handle_client(websocket, path):
    global websocket_robot1
    """
    Generic function for handling the communication between robot and clients
    """
    name = await websocket.recv()
    if(name == f"robot1_camera_client"):
        await asyncio.sleep(0.2)  # 30 fps
        camera_client = robot_camera_client()
        name = name + "_" + str(robot_camera_client.count)
        print(datetime.now().strftime("%c") + f" {name} is connected")
        robot1.stream_mode = True
        robot1.is_alive = True
        while(1):
            try:
                if(robot1.is_alive):
                    await websocket.send(robot1.get_frame().tobytes())
                else:
                    await websocket.send("")
                await asyncio.sleep(0.02)  # 30 fps
            except (websockets.exceptions.ConnectionClosedOK, websockets.ConnectionClosedError):
                print(datetime.now().strftime("%c")+f" {name} connection closed")
                del camera_client
                if(robot_camera_client.count == 0):
                    print(datetime.now().strftime("%c")+" Last listener closed the connection")
                    robot1.stream_mode = False
                break
    if(name == f"robot1"):
        print(datetime.now().strftime("%c")+f" {name} is connected")
        robot1.is_alive = True
        websocket_robot1 = websocket
        while(1):
            if(robot1.stream_mode):
                print(datetime.now().strftime("%c")+" sending start cmd to robot")
                await websocket.send("start")
                while(robot1.stream_mode):
                    try:
                        msg = await websocket.recv()
                        # print(type(msg),len(msg))
                        frame = np.frombuffer(msg, dtype=np.uint8)
                        frame = cv2.imdecode(frame, 1)
                        robot1.set_frame(frame)
                        await websocket.send("start")
                    except:
                        print(datetime.now().strftime("%c")+f" {name} is disconnected")
                        robot1.is_alive = False
                        return
            try:
                await websocket.ping()
            except (websockets.exceptions.ConnectionClosedOK, websockets.ConnectionClosedError):
                print(datetime.now().strftime("%c")+f" {name} is disconnected")
                robot1.is_alive = False
                return
            await asyncio.sleep(1)  # ping intervaltry:
    if(name == f"robot1_route_sender"):
        print(f"-- {name} is connected")
        if(robot1.is_alive):
            print("Robot1 is alive")
            await websocket_robot1.send("route_update")
            await websocket.send("ok")
        else:
            await websocket.send("failed")


# If SSL is needed be enabled set this flag to true. By default it is False
is_ssl_set = False
if __name__ == "__main__":
    init_robot_instances()
    init_host()
    if(is_ssl_set):
        start_server = websockets.serve(handle_client, ws_host_ip, ws_host_port, max_size=2**40, ssl=context)
    else:
        start_server = websockets.serve(handle_client, ws_host_ip, ws_host_port, max_size=2**40)
    asyncio.get_event_loop().run_until_complete(start_server)
    try:
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        print("\nCTRLC is pressed exiting")
