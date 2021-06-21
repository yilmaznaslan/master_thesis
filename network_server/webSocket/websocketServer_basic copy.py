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


class robot:
    """
    Robot class is used to handle each robot object. Although in the current state of the project there is only one robot,
    for simulating purposes or in a future scenerio with multiple robots, robot objects will be useful
    """
    count = 0
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.is_alive = False
        robot.count  = robot.count +1

    def get_total_count(self):
        print(robot.count)

    def set_frame(self,frame):
        self.frame = frame

    def get_frame(self):
        return self.frame
# Fundamental GLobal variables ###### OKAY
robot1_frame = np.ones((640, 480, 3))*150
robot1_listener_count = 0
robot1_stream_update = False
robot1_stream = False
robot1_alive = False
websocket_robot1 = None


# Get and set Robot alive
def robot1_alive_get():
    global robot1_alive
    return robot1_alive


def robot1_alive_set(status: bool):
    global robot1_alive
    robot1_alive = status

# Get and set the Frames


def frame_get():
    global robot1_frame
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 65]
    frame = cv2.imencode('.jpg', robot1_frame, encode_param)[1]
    return frame


def frame_set(frame):
    global robot1_frame
    robot1_frame = frame

# Functions for handling start,stop  informations of streaming frame


def robot1_stream_set(action):
    global robot1_stream
    robot1_stream = action


def robot1_stream_get():
    global robot1_stream
    return robot1_stream


# Fucntions for handling robot listeners
def robot1_listener_add():
    global robot1_listener_count
    robot1_listener_count = robot1_listener_count + 1


def robot1_listener_remove():
    global robot1_listener_count
    robot1_listener_count = robot1_listener_count - 1


def robot1_listener_get_count():
    global robot1_listener_count
    return robot1_listener_count


async def handle_client(websocket, path):
    global error_frame
    global websocket_robot1
    """
    Generic function for handling the communication between robot and clients
    """
    name = await websocket.recv()
    if(name == f"robot1_listener"):
        await asyncio.sleep(0.2)  # 30 fps
        robot1_listener_add()
        name = name + "_" + str(robot1_listener_get_count())
        print(f"-- {name} is connected")
        robot1_stream_set(True)
        while(1):
            try:
                if(robot1_alive_get()):
                    await websocket.send(frame_get().tobytes())
                else:
                    await websocket.send("")
                await asyncio.sleep(0.02)  # 30 fps
            except (websockets.exceptions.ConnectionClosedOK, websockets.ConnectionClosedError):
                print(f"-- {name} connection closed")
                robot1_listener_remove()
                if(robot1_listener_get_count() == 0):
                    print("-- Last listener closed the connection")
                    robot1_stream_set(False)
                break
    if(name == f"robot1"):
        print(f"-- {name} is connected")
        robot1_alive_set(True)
        websocket_robot1 = websocket
        while(1):
            if(robot1_stream_get()):
                print("-- sending start cmd to robot")
                await websocket.send("start")
                while(robot1_stream_get()):
                    try:
                        msg = await websocket.recv()
                        # print(type(msg),len(msg))
                        frame = np.fromstring(msg, dtype=np.uint8)
                        frame = cv2.imdecode(frame, 1)
                        frame_set(frame)
                        await websocket.send("start")
                    except:
                        print(f"-- {name} is disconnected")
                        robot1_alive_set(False)
                        return
            try:
                await websocket.ping()
            except (websockets.exceptions.ConnectionClosedOK, websockets.ConnectionClosedError):
                print(f"-- {name} is disconnected")
                robot1_alive_set(False)
                return
            await asyncio.sleep(1)  # ping intervaltry:
    if(name == f"robot1_route_sender"):
        print(f"-- {name} is connected")
        if(robot1_alive_get()):
            print("Robot1 is alive")
            await websocket_robot1.send("route_update")
            await websocket.send("ok")
        else:
            await websocket.send("failed")


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
    global robot1
    robot1 = robot(1,"robot1_real")
def set_context():
    """
    Context settings in case SSL encryption is needed. Please make sure to use correct private key for server.
    """

    global context
    path = os.environ['murmel_application_server']
    print('path to env variable'+os.environ['murmel_application_server'])
    context = ssl.SSLContext()
    context.load_cert_chain(path+'/certificates/cert.crt', path+'/certificates/private.key')


# If SSL is needed be enabled set this flag to true. By default it is False
is_ssl_set = False
if __name__ == "__main__":
    init_robot_instances()
    asd = robot(12,"asd")
    asd.get_total_count()

    pas = robot(23,"robot2")
    pas.get_total_count()

    print(robot1.name)
    init_host()
    # if(is_ssl_set):
    #     start_server = websockets.serve(handle_client, ws_host_ip, ws_host_port, max_size=2**40, ssl=context)
    # else:
    #     start_server = websockets.serve(handle_client, ws_host_ip, ws_host_port, max_size=2**40)
    # asyncio.get_event_loop().run_until_complete(start_server)
    # try:
    #     asyncio.get_event_loop().run_forever()
    # except KeyboardInterrupt:
    #     print("\nCTRLC is pressed exiting")
