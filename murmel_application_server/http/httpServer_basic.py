from flask import Flask, render_template, Response, request
import os
import ssl

path = "/root/murmel/servers/"
context =  ssl.SSLContext()
context.load_cert_chain(path+'/certificates/cert.crt',path+'/certificates/private.key')
http_host ="murmel.website"
http_port = 443

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

@app.route('/route_service/response/robot1',methods = ['POST', 'GET'])
def route_service_response_robot1():
    return render_template('route_service/route_response_robot1.html')


if __name__ == '__main__':
    # app.run(host=http_host, port=flask_port ,debug=True)
    # server = pywsgi.WSGIServer(('127.0.0.1',5000), app)
    # server.serve_forever()
   # context = ssl.Context(SSL.PROTOCOL_TLSv1_2)
   # context.use_privatekey_file("server.key")
   # context.use_certificate_file("server.crt")
    app.run(host=http_host, port=http_port, debug=True, ssl_context=context)
