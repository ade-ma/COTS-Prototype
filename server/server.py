from flask import Flask, request
from flask.ext.cors import CORS, cross_origin
import csv
import time
from outlet import Outlet
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
	
	# format in milliseconds from epoch
	ts = int(time.time()*1000)

	#Add data to volitile log
	tempLog.append(['temp', ts, sensorID, sensorValue])

	#Write sensorValue to CSV
	with open('log.csv', 'a') as csvfile:
	    writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
	    writer.writerow(['temp', str(ts), sensorID, sensorValue])

	return "Sensor " + str(sensorID) + " is reporting a temperature of " + str(sensorValue) + " degrees."
	
	csvfile.close()


@app.route('/humiditySense', methods=['GET', 'POST'])
def humiditySense():
	sensorID = request.args.get('ID')
	sensorValue = request.args.get('value')
	
	# format in milliseconds from epoch
	ts = int(time.time()*1000)

	#Add data to volitile log
	humidityLog.append(['humidity', ts, sensorID, sensorValue])

	#Write sensorValue to CSV
	with open('log.csv', 'a') as csvfile:
	    writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
	    writer.writerow(['humidity', str(ts), sensorID, sensorValue])

	return "Humidity sensor " + str(sensorID) + " is reporting a humidity of " + str(sensorValue) + "%."
	
	csvfile.close()


#######################################################################################
## These endpoints return data from the sensor requested ##
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

DEFAULT_RANGE = '6' # number of hours
@app.route('/rangeHumidity', methods=['GET', 'POST'])
def rangeHumidity():
	sensorID = request.args.get('ID')
	hours = float(request.args.get('hours', DEFAULT_RANGE)) 
	
	seconds = 3600*hours
	cutoff = 1000*(time.time() - seconds)
	# filter to correct date range and just the sensor we want
	recent = [data for data in humidityLog if data[2]==sensorID and int(data[1]) >= cutoff]
	
	if len(recent) != 0:
	    condensed = ['--'.join([str(x[1]), str(x[3])]) for x in compress(lpass(recent))]
	    response = ';'.join(condensed)
	    return response
	
	return "E"

@app.route('/rangeTemperature', methods=['GET', 'POST'])
def rangeTemperature():
	sensorID = request.args.get('ID')
	hours = float(request.args.get('hours', DEFAULT_RANGE)) 
	
	seconds = 3600*hours
	cutoff = 1000*(time.time() - seconds)
	
	# filter to correct date range and just the sensor we want
	recent = [data for data in tempLog if data[2]==sensorID and int(data[1]) >= cutoff]
	
	if len(recent) != 0:	    
	    condensed = ['--'.join([str(x[1]), str(x[3])]) for x in compress(lpass(recent))]
	    response = ';'.join(condensed)
	    return response
	
	return "E"

@app.route('/lastCommand', methods=['GET', 'POST'])
def lastCommand():
	deviceID = request.args.get('ID')
	for command in commandLog[::-1]:
		if command[2] == deviceID:
			return command[3]
	return "E"

def compress(data):
    """
    remove middle points in colinear sets of three
    """
    new_data = list(list(x) for x in data)
    
    def x_val(datum): # timestamp
        return float(datum[1])
    
    def y_val(datum): #sensor-value
        return float(datum[3])
    
    def slope(datum1, datum2):
        dy = (y_val(datum2) - y_val(datum1))
        dx = (x_val(datum2) - x_val(datum1))
        return dy/dx
      
    # remove middle points in colinear sets of three
    index = 1
    while index < len(data)-1:
        slope_left = slope(new_data[index - 1], new_data[index])
        slope_right = slope(new_data[index], new_data[index+1])
        
        if slope_left == slope_right:
            new_data.pop(index)
        
        else:
            index += 1
        
    return new_data
    
def compress_lossy(data, max_length):
    """
    Compress to a given length, probably lossy
    
    The strategy is to replace clusters of points by the average
    """
    
    def x_val(datum): # timestamp
        return float(datum[1])
    
    def y_val(datum): #sensor-value
        return float(datum[3])
    
    def replace_y(datum, new_y): #change out for new value
        datum[3] = new_y
    
    def replace_x(datum, new_x):
        datum[1] = new_x
    
    def condense_block(block):
        x_vals = [x_val(datum) for datum in block]
        y_vals = [y_val(datum) for datum in block]
        
        x_ave = sum(x_vals)/float(len(x_vals))
        y_ave = sum(y_vals)/float(len(y_vals))
        
        # copy the format, but make the point average
        new_datum = list(data[0])
        replace_y(new_datum, y_ave)
        replace_x(new_datum, x_ave)
        
        return new_datum
    
    new_data = []
    
    block_size = int(round(len(data)/float(max_length)))
    index = block_size
    while index < len(data):
        
        block = data[index - block_size: index]
        new_data.append(condense_block(block))
        index += block_size
    
    # turn the remaining points into a block, but we want the final x-value
    # to be the same as the original, since it is the most recent
    index -= block_size;
    last_block = data[index:]
    new_data.append(lpass(last_block)[-1])
    
    return new_data

def lpass(data):
    """
    low-pass noisy data with simple FIR
    """
    
    new_data = list(list(x) for x in data)
    
    kernel = [1, 2, 3, 3]
    kernel = [x/float(sum(kernel)) for x in kernel]
    
    index = len(kernel) -1
    while index < len(data):
        ave = 0
        for i in range(len(kernel)):
            ave += float(data[index - (len(kernel)-1) + i][3])*kernel[i]
        
        new_data[index][3] = ave
        index+=1
    
    return new_data


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

outlets = {'Lights':'94:10:3e:30:8f:69'}


if __name__ == '__main__':

	app.debug = True
	app.run(host='0.0.0.0',port=8000)
