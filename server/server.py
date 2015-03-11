from flask import Flask, request
import csv
import time
app = Flask(__name__)

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
	ts = time.time()

	#Add data to volitile log
	tempLog.append(['temp', ts, sensorID, sensorValue])

	#Write sensorValue to CSV
	with open('log.csv', 'a') as csvfile:
	    writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
	    writer.writerow(['temp', ts, sensorID, sensorValue])

	return "Sensor " + str(sensorID) + " is reporting a temperature of " + str(sensorValue) + " degrees."


@app.route('/humiditySense', methods=['GET', 'POST'])
def humiditySense():
	sensorID = request.args.get('ID')
	sensorValue = request.args.get('value')
	ts = time.time()

	#Add data to volitile log
	humidityLog.append(['humidity', ts, sensorID, sensorValue])

	#Write sensorValue to CSV
	with open('log.csv', 'a') as csvfile:
	    writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
	    writer.writerow(['humidity', ts, sensorID, sensorValue])

	return "Humidity sensor " + str(sensorID) + " is reporting a humidity of " + str(sensorValue) + "%."


#######################################################################################
## These endpoints return just the most recent sensor value for the sensor requested ##
#######################################################################################

@app.route('/lastTemp', methods=['GET', 'POST'])
def lastTemp():
	sensorID = request.args.get('ID')
	for measurement in tempLog[::-1]:
		if measurement[2] == sensorID:
			return measurement[3]
	return "E"

@app.route('/lastHumidity', methods=['GET', 'POST'])
def lastHumidity():
	sensorID = request.args.get('ID')
	for measurement in humidityLog[::-1]:
		if measurement[2] == sensorID:
			return measurement[3]
	return "E"

@app.route('/lastCommand', methods=['GET', 'POST'])
def lastCommand():
	deviceID = request.args.get('ID')
	for command in commandLog[::-1]:
		if command[2] == deviceID:
			return command[3]
	return "E"


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
    log = list(reader)

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