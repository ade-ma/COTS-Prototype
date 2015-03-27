from miranda import upnp
import os
import re
import subprocess

def getIP(MAC):
    """
    finds the ip of the mac address
    """
    
    possible_ips = ['192.168.1.' + str(x) for x in range(100,110)]
    
    for ip in possible_ips:
        if getMAC(ip) == MAC:
            return ip
    
    return None

def getMAC(ip):
    """
    finds MAC of the ip address
    """
    
    # first we add the ip to the arp cache by pinging it
    # we also supress the printed output of the ping
    devnull = open(os.devnull, "w")
    subprocess.call(["ping", "-c", "2", ip], stdout=devnull)
    
    # now arp it
    pid = subprocess.Popen(["arp", "-n", ip], stdout=subprocess.PIPE)
    output = pid.communicate()[0]
    
    # find the MAC with regex
    results = re.search(r"(([a-f\d]{1,2}\:){5}[a-f\d]{1,2})", output)
    if not(results is None):
        MAC = results.groups()[0]
    else:
        MAC = None
    
    devnull.close()
    return MAC

def getPort(ip, ports):
    """
    Get the active port for a wemo switch
    """
    open_port = None
    for port in ports:
        pid = subprocess.Popen(["curl","-s","-m", "5", ip+":"+port], stdout=subprocess.PIPE)
        output = pid.communicate()[0]

        # a 404 reponse means right port
        if "404 Not Found" in output:
            open_port = port
            break

    return open_port


class MACNotFoundError(Exception):
    pass

class WemoPortsClosedError(Exception):
    pass

class Outlet:
    """
    Class represents a Belkin WeMo wireless outlet.
    """
    def __init__(self, MAC):
        """
        MAC address of the switch
        """
        
        self.MAC = MAC
        
        print str.format("Aqcuiring IP address for switch {}", MAC)
        self.ip = getIP(MAC)
        if self.ip is None:
            raise MACNotFoundError(str.format("device with MAC address '{}' not found on the local network", MAC))
        print str.format("IP: {}", self.ip)
        
        print "finding port"
        self.ports = [str(x) for x in range(49152,49154)]
        self.port = getPort(self.ip, self.ports)
        if self.port is None:
            raise WemoPortsClosedError(str.format("Can't find open ports for switch {}",self.MAC))
        print str.format("port: {}", self.port)
        
        self.conn = upnp(self.ip, self.port, None,False)
    
    def turnOn(self):
        resp = self.conn.sendSOAP(self.ip + ':' + self.port, 'urn:Belkin:service:basicevent:1', 
            'http://' + self.ip + ':' + self.port + '/upnp/control/basicevent1', 
            'SetBinaryState', {'BinaryState': (1, 'Boolean')})
    
    def turnOff(self):
        resp = self.conn.sendSOAP(self.ip + ':' + self.port, 'urn:Belkin:service:basicevent:1', 
            'http://' + self.ip + ':' + self.port + '/upnp/control/basicevent1', 
            'SetBinaryState', {'BinaryState': (0, 'Boolean')})
    
    def getState(self):
        resp = self.conn.sendSOAP(self.ip + ':' + self.port, 'urn:Belkin:service:basicevent:1', 
            'http://' + self.ip + ':' + self.port + '/upnp/control/basicevent1', 
            'GetBinaryState', {'BinaryState': (1, 'Boolean')})
        
        if "<BinaryState>0</BinaryState>" in resp:
            state = 0
            print "outlet off"
        else:
            state = 1
            print "outlet on"
        
        return state;

if __name__ == '__main__':
    import time
    MAC = '94:10:3e:30:8f:69'    
    sw = Outlet(MAC)
    sw.turnOn();
    time.sleep(1);
    sw.getState();
    sw.turnOff()
    time.sleep(1);
    sw.getState();
    
