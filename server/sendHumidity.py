import urllib2
import sys
from dropletConfig import DROPLET_IP
farm = 'olin' # 'tangerinis' # 'firstlight'
ID = sys.argv[1]
value = sys.argv[2]
url = "http://"+DROPLET_IP+"/humiditySense?ID=" + ID + "&value=" + value + "&farm=" + farm
print url
urllib2.urlopen(url)
