from miranda import upnp

class Outlet:
    """
    Class represents a Belkin WeMo wireless outlet.
    """
    def __init__(self, ip, port='49153'):
        self.ip = ip
        self.port = port
        self.conn = upnp(ip, port, None,False)
    
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
    ip = '192.168.1.100'    
    sw = Outlet(ip)
    sw.turnOn();
    time.sleep(1);
    sw.getState();
    sw.turnOff()
    time.sleep(1);
    sw.getState();
    
