"""
This script creates a Flask applcation to host two different services to users-

- Camera Service
- Route Update Service

"""

from flask import Flask, render_template, Response, request
import os
import ssl
import socket


# Create a Flask App
app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/camera_service')
def camera_service():
    return render_template('camera_service/video_index.html')


@app.route('/camera_service/robot1')
def camera_service_robot1():
    return render_template('camera_service/video_robot1.html')


@app.route('/camera_service/robot2')
def camera_service_robot2():
    return render_template('camera_service/video_robot2.html')


@app.route('/route_service')
def route_service():
    return render_template('route_service/route_index.html')


@app.route('/route_service/request/robot1')
def route_service_request_robot1():
    return render_template('route_service/route_request_robot1.html')


@app.route('/route_service/response/robot1', methods=['POST', 'GET'])
def route_service_response_robot1():
    return render_template('route_service/route_response_robot1.html')


def init_host():
    global http_host_name, http_host_ip, http_host_port

    # Replace IP address with the public IP address or host name of the server machine
    http_host_name = socket.gethostname()
    http_host_ip = socket.gethostbyname(http_host_name)
    http_host_port = 8080


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
if __name__ == '__main__':
    init_host()
    if(is_ssl_set):
        set_context()
        app.run(host=http_host_ip, port=http_host_port, debug=True, ssl_context=context)
    else:
        app.run(host=http_host_ip, port=http_host_port, debug=True)
