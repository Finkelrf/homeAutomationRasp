import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import time
import datetime
import subprocess 
import atexit
from os.path import exists

class WheelManager:
	distance_total = 0
	PATH_LOG_FILE = ""

	# The callback for when the client receives a CONNACK response from the server.
	def on_connect(self,client, userdata, flags, rc):
	    print("Connected with result code "+str(rc))

	    # Subscribing in on_connect() means that if we lose the connection and
	    # reconnect then subscriptions will be renewed.
	    client.subscribe("home/hamster/wheel/distance",1)

	# The callback for when a PUBLISH message is received from the server.
	def on_message(self,client, userdata, msg):
	    print(msg.topic+" "+str(msg.payload))
	    self.distance_total = self.distance_total+float(msg.payload)
	    ts = time.time()
	    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
	    speed = float(msg.payload)/60
	    string = st+" "+str(self.distance_total)+" "+str(speed)+"\n"
	    with open(mountPath+"logHamsterWheel.txt", "a") as myfile:
	    	myfile.write(string)

	    if float(msg.payload) != 0:
	    	publish.single("home/hamster/wheel/distance_total", distance_total, qos=1, hostname="192.168.1.12",port=1883)

	def check_initial_distance(self,filePath):
		path = filePath

		if exists(path):
			with open(path, 'r') as myfile:
			    data=myfile.read()
			if data != "":
				lines = []
				lines = data.split("\n")
				rows = lines[-2].split(" ")
				self.distance_total = float(rows[2])
				print "Distance total read: "+str(self.distance_total)
			else:
				print "file is empty"
		else:
			print "file doesn't exist"

	def __init__(self,mountPath):
		self.PATH_LOG_FILE = mountPath
		self.check_initial_distance(mountPath+"logHamsterWheel.txt")
		client = mqtt.Client()
		client.on_connect = self.on_connect
		client.on_message = self.on_message

		client.connect("127.0.0.1", 1883, 60)

		# Blocking call that processes network traffic, dispatches callbacks and
		# handles reconnecting.
		# Other loop*() functions are available that give a threaded interface and a
		# manual interface.
		client.loop_forever()


class Mounter:
	mounted = False
	@staticmethod
	def mount(mountPath):
		cmdList = []
		cmdList.append("./mountDrive.sh")
		cmdList.append(mountPath)
		proc = subprocess.Popen(cmdList, stdout=subprocess.PIPE)
		ret = proc.stdout.read()
		ret = ret.replace("\n","")
		if ret == "OK":
			Mounter.mounted = True
			return True
		else:
			Mounter.mounted = False
			return False


	@staticmethod
	def umount(mountPath):
		if Mounter.mounted == True:
			cmdList = []
			cmdList.append("./umountDrive.sh")
			cmdList.append(mountPath)
			proc = subprocess.Popen(cmdList, stdout=subprocess.PIPE)
			ret = proc.stdout.read()
			ret = ret.replace("\n","")
			if ret == "OK":
				return True
			else:
				return False
		else:
			print "Nothing was mounted"
			return False

def exit_handler():
    ret = Mounter.umount(mountPath)
    if ret == True:
    	print "Umounting Success"



if __name__ == "__main__":
	atexit.register(exit_handler)
	mountPath = "usbDrive/"
	if exists(mountPath+"logHamsterWheel.txt") == False:
		print "External drive is not connected, saving locally"
		mountPath = "usbDrive/"

	wm = WheelManager(mountPath)


	



