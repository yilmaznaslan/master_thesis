## Overview

<img src="images/murmel_servers_overview.png", width="500" >
The purpose of the HTTP Server is to establish a user interface for the communication between robot other browser based clients. As an output of the developed HTTP Server three different services are created as below;
- Camera Streaming Service
- Route Updating Serviice

### Camera Streaming Service
Camera Streaming Service enables users to access robots camera to control the video stream from robot to the murmel application server. Through the created HTML files users can easily start or stop the video stream from robot upon succesfully enabling Javascript to establish connections to WebSocket Server.


### Route Update Service
Route Update Service enables users to send route/task files to the robot.


## Installation
For the installation of the Server application, following external libraries are needed to be installed.
- HTTP Server [more details about the library](https://pypi.org/project/Flask/)
  - pip install Flask

### Note
If you wish to use use SSL Encryption to enable enable WebSocket communication, note the following issues.
- Please make sure that an environment variable for referring to the  *murmel_application_server* repository is already created.
- Create a prive key for the host name and save it under certificates folder.

