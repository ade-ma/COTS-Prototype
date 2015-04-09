import urllib2
import sys
from dropletConfig import DROPLET_IP

ID = sys.argv[1]
value = sys.argv[2]
url = "http://"+DROPLET_IP+"/humiditySense?ID=" + ID + "&value=" + value
print url
urllib2.urlopen(url)
