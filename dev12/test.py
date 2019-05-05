from subprocess import check_output
# from PyAccessPoint import pyaccesspoint
from flask import Flask, request, render_template
import time
import socket

# access_point = pyaccesspoint.AccessPoint()
# access_point.stop()
# access_point.start()
#

debug_on_windows = True

if debug_on_windows:
    hostname = socket.gethostname()
    ip_addr = socket.gethostbyname(hostname)
else:
    ip_addr = check_output(['hostname', '-I']).decode('ascii')


print("ip => ", ip_addr)
app = Flask(__name__)



@app.route('/hello')
def hello():
    return "Hello World!"

@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')

@app.route('/connect', methods=['POST'])
def connect():
    # ssid = request.args.get('ssid')
    # password = request.args.get('password')

    ssid = request.form['ssid']
    password = request.form['password']
    print("/connect")
    print("\tssid => ", ssid)
    print("\tpassword => ", password)

    return "Try to connect to SSID = "+ssid+""


if __name__ == '__main__':
    app.run(host=ip_addr)
