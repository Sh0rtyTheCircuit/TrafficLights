### WEBSERVER SETUP ###
import socket
import select
import sys
import threading

### LED SETUP ###
import RPi.GPIO as GPIO			#RPi for Raspberry Pi
import time
GPIO.setmode(GPIO.BCM)


GPIO.setwarnings(False)			#Turn off warnings
GPIO.setup(4,GPIO.OUT) 			#GREEN
GPIO.setup(17,GPIO.OUT) 		#YELLOW
GPIO.setup(22,GPIO.OUT)			#RED


def OFF():				#Turn all lights off
	
	GPIO.output(4,GPIO.LOW)
	GPIO.output(17,GPIO.LOW)
	GPIO.output(22,GPIO.LOW)
	
def GREEN():				#Only Green is on
	OFF()
	GPIO.output(4,GPIO.HIGH)
	
def YELLOW():				#Only Yellow is on
	OFF()
	GPIO.output(17,GPIO.HIGH)
	
def RED():				#Only Red is on
	OFF()
	GPIO.output(22,GPIO.HIGH)
	
def CYCLE(client,stopper):				#Green to Yellow to Red Repeat 
	while not stopper.is_set():		#Listen for stopper. As long as stopper is not set, will continue loop
		OFF()
		GPIO.output(4,GPIO.HIGH)
		time.sleep(3)
		OFF()
		GPIO.output(17,GPIO.HIGH)
		time.sleep(3)
		OFF()
		GPIO.output(22,GPIO.HIGH)
		time.sleep(3)
		#return 0	

## CREATE WEBSERVER ##

HOST, PORT = '', 9898 

listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)	#socket setup
listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
listener.bind((HOST,PORT))					#Where the server is now located
listener.listen(1)						#Listen for this many clients

print 'Listener is set up'
stopper = threading.Event()					#Handler for starting and stopping the thread

while True:
	client_connection, client_address = listener.accept()	#Accept connection from user 
	'''TIMEOUT
	client_connection.setblocking(0)			#If does not receive anything from client, will continue code
	request = "post /clear  "				#default request
	ready = select.select([client_connection],[],[],0)	#Looking every One second for a different client request
	if ready[0]:'''						#If client sends new request	
	request = client_connection.recv(1024)			#Waiting for GET REQUEST(refresh/load website). Request is new request now.
	print request						#Request = whatever is Posted when btns are pressed
	check_status = request[0:13]
	print check_status
	if check_status.find("green")>0:			#Look for "Green" in request. If not found, will return -1 which breaks the code
		stopper.set()
		GREEN()
	if check_status.find("yellow")>0:
		stopper.set()
		YELLOW()
	if check_status.find("red")>0:
		stopper.set()
		RED()
	if check_status.find("cycle")>0:
		stopper.clear()
		cycle_handler = threading.Thread(target=CYCLE,args=(client_connection,stopper))
		cycle_handler.start()
	if check_status.find("reset")>0:
		stopper.set()
		OFF() 
	disp_body = """\
<html>
	<title> Choose Wisely </title>
	<body>

		<form action="http://localhost:9898/green" method= "post">
			<button>Green</button>
		</form>
	<br>
		<form action="http://localhost:9898/yellow" method= "post">
			<button> Yellow </button>
		</form>
	<br>
		<form action="http://localhost:9898/red" method= "post">
			<button> Red </button>
		</form>
	<br>
		<form action="http://localhost:9898/cycle" method= "post">
			<button> Cycle </button>
		</form>
	<br>
		<form action="http://localhost:9898/reset" method= "post">
			<button> Reset </button>
		</form>
	</body>

</html>	
	"""
        display = """\
HTTP/1.1 302 OK
Content-Type: text/html
Content-Length: %d
Connection: close  
""" % len(disp_body)

	client_connection.sendall(display + disp_body)
	client_connection.close()
	
	
	
