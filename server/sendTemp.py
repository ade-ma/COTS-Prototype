import urllib2
import sys
from dropletConfig import DROPLET_IP
farm = 'tangerinis' # 'firstlight'
ID = sys.argv[1]
value = sys.argv[2]
url = "http://" + DROPLET_IP + "/tempSense?ID=" + ID + "&value=" + value + "&farm=" + farm
urllib2.urlopen(url)
