from flask import Flask, request
from flask.ext.cors import CORS, cross_origin
import csv
import time
#from outlet import Outlet
import subprocess
app = Flask(__name__)
cors = CORS(app)

#########################################################################################
##
## Before running, create an empty file log.csv in your server directory.
##
## Sensors should hit endpoints:
## Humidity Sensor Example: 192.168.1.4/humiditySense?ID=214&value=125
## Temperature Sensor Example: 192.168.1.4/tempSense?ID=412&value=70
##
## To get the most recent temperature measured by a specific sensor, use endpoint:
## Example: http://192.168.1.4/lastHumidity?ID=214
## Example: http://192.168.1.4/lastTemp?ID=214
##
## For debugging, if you'd like to see all logs, use:
## Example: http://192.168.1.4/getLogs
##
##########################################################################################

@app.route('/', methods=['GET', 'POST'])
def status():
    return 'Your Sproutwave Server is Running!'

###########################################################################
## These endpoints accept data from sensors and store the data in a csv. ##
###########################################################################

@app.route('/tempSense', methods=['GET', 'POST'])
def tempSense():
	sensorID = request.args.get('ID')
	sensorValue = request.args.get('value')
	command = "python sendTemp.py " + str(sensorID) + " " + str(sensorValue)

	if sensorValue == "" or sensorValue is None or sensorID == "" or sensorID is None:
		return "E"
	
	#Relay data to public server!
	subprocess.call(["python", "sendTemp.py", str(sensorID), str(sensorValue)])

	# format in milliseconds from epoch
	ts = int(time.time()*1000)

	#Add data to volitile log
	tempLog.append(['temp', ts, sensorID, sensorValue])

	#Write sensorValue to CSV
	with open('log.csv', 'a') as csvfile:
	    writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
	    writer.writerow(['temp', str(ts), sensorID, sensorValue])

	return "Sensor " + str(sensorID) + " is reporting a temperature of " + str(sensorValue) + " degrees."


@app.route('/humiditySense', methods=['GET', 'POST'])
def humiditySense():
	sensorID = request.args.get('ID')
	sensorValue = request.args.get('value')
	
	if sensorValue == "" or sensorValue is None or sensorID == "" or sensorID is None:
		return "E"
	
	#Relay data to public server!
	subprocess.call(["python", "sendHumidity.py", str(sensorID), str(sensorValue)])
	
	# format in milliseconds from epoch
	ts = int(time.time()*1000)

	#Add data to volitile log
	humidityLog.append(['humidity', ts, sensorID, sensorValue])

	#Write sensorValue to CSV
	with open('log.csv', 'a') as csvfile:
	    writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
	    writer.writerow(['humidity', str(ts), sensorID, sensorValue])

	return "Humidity sensor " + str(sensorID) + " is reporting a humidity of " + str(sensorValue) + "%."


#######################################################################################
## These endpoints return just the most recent sensor value for the sensor requested ##
#######################################################################################

@app.route('/lastTemperature', methods=['GET', 'POST'])
def lastTemp():
	sensorID = request.args.get('ID')
	for measurement in tempLog[::-1]:
		if measurement[2] == sensorID:
			return str(measurement[1]) + '--' + str(measurement[3])
	return "E"

@app.route('/lastHumidity', methods=['GET', 'POST'])
def lastHumidity():
	sensorID = request.args.get('ID')
	for measurement in humidityLog[::-1]:
		if measurement[2] == sensorID:
			return str(measurement[1]) + '--' + str(measurement[3])
	return "E"

@app.route('/lastCommand', methods=['GET', 'POST'])
def lastCommand():
	deviceID = request.args.get('ID')
	for command in commandLog[::-1]:
		if command[2] == deviceID:
			return command[3]
	return "E"

##########################################################
## This endpoint turns off and on the swiwtch for the demo
##########################################################

@app.route('/toggleOutlet', methods=['GET','POST'])
def toggleOutlet():
    factor = request.args.get('factor')
    outlet = outlets.get(factor)
    if not outlet is None: 
        if outlet.getState() == 1:
            outlet.turnOff()
            return('Outlet now on')
        else:
            outlet.turnOn()
            return('Outlet now off')
    
    else:
        msg = "no outlets set up for " + factor
        print msg
        return msg
    

###################################
## This endpoint prints all logs ##
###################################

@app.route('/getLogs', methods=['GET', 'POST'])
def getLogs():
	result = ""
	for i in tempLog:
		result = result + str(i) + '<br>'
	for i in humidityLog:
		result = result + str(i) + '<br>'
	for i in commandLog:
		result = result + str(i) + '<br>'
	return result


#################################################################################
## Initialize server by loading historical data from CSV and splitting it into ##
## separate logs for different data types									   ##
#################################################################################

with open('log.csv', 'rb') as f:
    reader = csv.reader(f)
    try:
    	log = list(reader)
    except:
	log = []

tempLog = []
humidityLog = []
commandLog = []

for i in log:
	if i[0] == 'temp':
		tempLog.append(i)
	if i[0] == 'humidity':
		humidityLog.append(i)
	if i[0] == 'command':
		commandLog.append(i)



if __name__ == '__main__':

	app.debug = True
	app.run(host='0.0.0.0')
	
	     
