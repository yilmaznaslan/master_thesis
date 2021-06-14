import asyncio
import websockets
import cv2
import numpy as np
import random
import pickle
import ssl
import os

# Context settings in case SSL encryption is needed. Please make sure to use correct private key for server.
def set_context():
    global context
    path = os.environ['murmel_application_server']
    print('path to env variable'+os.environ['murmel_application_server'])
    context = ssl.SSLContext()
    context.load_cert_chain(path+'/certificates/cert.crt',
                            path+'/certificates/private.key')


# Replace IP address with the public IP address or host name of the server machine
ws_host = "127.0.0.1"
ws_port = 8000


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

# Generic function for handling the communication between robot and clients
async def handle_client(websocket, path):
    global error_frame
    global websocket_robot1
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


if __name__ == "__main__":
    print("Websocket Server started")
    #start_server = websockets.serve( handle_client, ws_host, ws_port, max_size=2**40,ssl= context)
    start_server = websockets.serve(
        handle_client, ws_host, ws_port, max_size=2**40)
    asyncio.get_event_loop().run_until_complete(start_server)
    try:
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        print("\nCTRLC is pressed exiting")
