#server file
import network
import socket
from time import sleep
import machine
from machine import Pin
import sys
import _thread

#set up the running guard to prevent errors
#main_runner = Pin(15, Pin.IN, Pin.PULL_UP)
#if main_runner.value() != 0:
#    print("Set GPIO15 to GND to run the program")
#    sys.exit()

ssid = 'raspberry Hotspot' #wifi network name
password = 'Wow this hotspot is so secure :)' #wifi password

led = Pin(13, Pin.OUT)

#connect to a wlan and return the ip adress
def connect(_ssid, _password):
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(_ssid, _password)
    #wait for connection
    max_wait = 10
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() > 3:
            break
        max_wait -= 1
        print('Waiting for connection...')
        sleep(1)
    
    if wlan.status() != 3:
        raise RuntimeError('network connection failed')
    else:
        print('connected')
        status = wlan.ifconfig()
        ip = status[0]
        print ('ip: ' + ip)
        led.value(1)
        return ip

#open a socket on port 80
def open_socket(_ip):
    address = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    connection = socket.socket()
    connection.bind(address)
    connection.listen(1)
    print('Listening on: ', address)
    return connection

#generate a html web page
def web_page(_lux):
    #html code to be server to the page
    html = f"""
            <!DOCTYPE html>
            <html>
            <body>
            <p>The light intensity is {_lux} lux</p>
            </body>
            </html>
            """
    return str(html)

#start a web server
def serve(_connection):
    lux = 1
    while True:#add a hardware shutdown
        client,addr = _connection.accept()
        print('Client connected from: ',addr)
        request = client.recv(1024)
        request = str(request)
        
        #send the response stuff here
        
        html = web_page(lux)
        client.send(html)
        
        print(request)
        client.close()

#all the code for the second thread goes here
def second_thread():
    #blink the led
    while True:
        led.value(1)
        sleep(0.25)
        led.value(0)
        sleep(0.25)

#main code
#_thread.start_new_thread(second_thread, ()) #start the second thread

try:
    ip = connect(ssid, password)
    connection = open_socket(ip)
    serve(connection)
except KeyboardInterrupt:
    machine.reset()
