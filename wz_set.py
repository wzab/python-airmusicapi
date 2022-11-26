"""
Test file to check functionality in Airmusic API towards Lenco DIR150BK.
"""

import sys

import json
import logging
import time
from airmusicapi import airmusic


#IPADDR = '192.168.2.147'  # Change this to the IP-address or hostname of your device.
IPADDR = sys.argv[1]  # Change this to the IP-address or hostname of your device.
TIMEOUT = 5  # in seconds. In most cases 1 second is sufficient.

am = airmusic(IPADDR, TIMEOUT)
am.log_level = logging.DEBUG
am.init(language="pl")

am.enter_menu(75)
ulub=am.get_menu(menu_id=75)

v=am.search_station(sys.argv[2])
print(v)
am.enter_menu(v['id'])
m=am.get_menu(menu_id=v['id'])
print(m)

#am.play_station(station_id)
#am.play_url(station_id) # Shows URL of the station stream
#am.set_volume(x) # 0-30

