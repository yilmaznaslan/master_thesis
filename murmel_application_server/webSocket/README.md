## Overview
The purpose of the WebSocket Server is to establish a communication channel between the Robot and application center to exchange large amount of information which can not be send by using MQTT or HTTP.	Following uses cases are utilized by using the WebSock Server.
- Enabling/Disabling Live video stream from robot
- Uploading Coordinate/Task file to the robot.
## Installation
For the installation of the Server application, following external libraries are needed to be installed.
- WebSocket Server[more details about the library,here](https://websockets.readthedocs.io/en/stable/intro.html) 
- Opencv[more details about the library,here](https://pypi.org/project/opencv-python/
### Note
If you wish to use use SSL Encryption to enable enable WebSocket communication, note the following issues.
- Please make sure that an environment variable for referring to the  *murmel_application_server* repository is already created.
- Create a prive key for the host name and save it under certificates folder.

