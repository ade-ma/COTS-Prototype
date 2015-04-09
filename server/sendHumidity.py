import urllib2
import sys

ID = sys.argv[1]
value = sys.argv[2]

urllib2.urlopen("http://104.131.30.130/humiditySense?ID=" + ID + "&value=" + value)
