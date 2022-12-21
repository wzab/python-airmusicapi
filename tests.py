"""
Test file to check functionality in Airmusic API towards Lenco DIR150BK.
"""

import sys

import json
import logging
import time
from airmusicapi import airmusic


#IPADDR = '192.168.2.147'  # Change this to the IP-address or hostname of your device.
#IPADDR = sys.argv[1]  # Change this to the IP-address or hostname of your device.
IPADDR = 'azradio.lan'
TIMEOUT = 5  # in seconds. In most cases 1 second is sufficient.


def api_init(ip, timeout):
    am = airmusic(ip, timeout)
    am.log_level = logging.DEBUG
    am.init(language="pl")
    return am


# Always pass 'am' as kwarg! Dont use positional args
def am_api(f):
    def inner(*args, **kwargs):
        am = kwargs.get('am',None)
        if not am:
            kwargs['am'] = api_init(IPADDR, TIMEOUT)
        return f(*args, **kwargs)
    return inner


def get_item(resp):
    try:
        item = resp['item']
    except KeyError:
        item = []
        logging.error(f"Received incomplete response: {resp}")
    
    if ((len(item) != int(resp['item_return'])) 
        or (len(item) != int(resp['item_total']))):
        logging.warning(f"Resp len: {len(item)}, "
                        f"item return: {resp['item_return']}, "
                        f"item total: {resp['item_total']}")
    
    # If list is not empty and has some missing fields
    if item and not all([('id' in f) and ('name' in f) for f in item]):
        logging.warning("Some items have missing id/name fields! \n"
                       f"{[f for f in item if ('id' not in f) or ('name' not in f)]}")
    
    return item


@am_api
def get_favs_raw(am):
    am.enter_menu(75)
    favs = am.get_menu(menu_id=75)
    
    return favs


@am_api
def discover_menus(am):
    def enter_and_get_nexts(am, i):
        am.enter_menu(menu_id=i)
        return am.get_menu(menu_id=i)
    
    def enter_nexts(am, node):
        resp = enter_and_get_nexts(am, node)
        if 'item' not in resp:
            return
        
        ret = []
        for i in item:
            ret.append(i)
            ret.append(enter_nexts(am, i))
        return ret
    
    enter_and_get_nexts(am, 1)
    
    # Recursively walk through the tree
    # Not tested!
    raise NotImplementedError


@am_api
def get_vol(am):
    return am.get_volume()

@am_api
def set_vol(am, v):
    if (v > 30) or (v < 0):
        logging.warning("Attempt to set  volume outside of 0-30 range!")
    _v = min(30, max(0, v))
    resp = am.set_volume(_v)
    return resp


@am_api
def get_mute(am):
    return am.mute

@am_api
def set_mute(am, mute):
    am.mute = mute


def get_favs(am=None):
    favs_raw = get_favs_raw(am=am)
    if not favs_raw:
        return []
        
    favs = get_item(favs_raw)
    
    return favs

@am_api
def set_fav(am, station_id):
    favs = get_favs()
    pos = len(favs)
    
    return am.set_favourite(station_id, pos)

@am_api
def del_fav(am, station_id):
    # https://github.com/RobinMeis/AirMusic/tree/master/docs
    raise NotImplementedError


@am_api
def search_stations(am, name):
    """!
    Return list of stations with substring in name
    @param am optional air_musicapi handle
    @param name substring with part of station name to look for
    """
    logging.debug(f"Searching: name = {name}")
    if not name: # if empty
        return []
    resp = am.search_station(name)
    logging.debug(f"Response: {resp}")
    try:
        menu_id = resp['id']
    except KeyError:
        logging.error(f"Response has no 'id' field! Resp: {resp}")
        raise
    
    am.enter_menu(menu_id=menu_id)
    resp = am.get_menu(menu_id=menu_id)
    # Nothing found: RESP = {'result': '100'}
    if 'result' in resp:
        return []
    
    ret = get_item(resp)
    if not isinstance(ret, list):
        ret = [ret]
    return ret


@am_api
def play_station(am, station_id):
    """!
    
    """
    return am.play_station(station_id)

def print_list(list_result):
    """!
    Show the response from a list command in pretty print format.
    @param list_result contains the result (dict) of the 'list' command.
    """
    if 'result' in list_result:
        print("Error: {}".format(list_result['result']))
        return
    print("List: {} out of {}:".format(list_result['item_total'], list_result['item_return']))
    for entry in list_result['item']:
        print("  {:5} {} -> {}".format(entry['id'], entry['name'], entry['status']))


def print_songinfo(api_ref):
    """!
    Print the song information, as far as it is available.
    @param api_ref is an Airmusic API instance.
    """
    print("Press CTRL-C to interrupt.")

    print("{:3} {:3} {}".format('Vol', 'sid', 'Status'))
    try:
        while True:
            playinfo = api_ref.get_playinfo()
            if 'result' in playinfo:
                print(" ... {}".format(playinfo['result']))
            else:
                status = "{:3} {:3} {} ".format(playinfo['vol'], playinfo['sid'], playinfo['status'])
                if 'artist' in playinfo:
                    status += "Artist:'{}' Song:'{}'".format(playinfo['artist'], playinfo['song'])
                print(status)
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass


def main():
    """
    Main part of the code. Checks some parts of the API against the Lenco DIR150BK radio.
    """
    # Create an API instance and setup initial communication with the device.
    am_obj = api_init(IPADDR, TIMEOUT)

    # Show device information.
    print('Device Name: %s' % am_obj.friendly_name)
    print(json.dumps(am_obj.get_systeminfo(), indent=2))

    # Show volume and mute levels.
    print("Current volume = {}".format(am_obj.volume))
    print("Current mute = {}".format(am_obj.mute))

    # Show the content of the hotkeylist.
    hotkeylist = am_obj.get_hotkeylist()
    if hotkeylist:
        print("Hotkeylist: {} out of {}:".format(hotkeylist['item_total'], hotkeylist['item_return']))
        for itm in hotkeylist['item']:
            print("  {}, {}, {}".format(itm['id'], itm['name'], itm['status']))

    print("Verify navigation through menus to reach a station to play.")
    print_list(am_obj.get_menu(menu_id=1))
    am_obj.enter_menu(52)
    print_list(am_obj.get_menu(menu_id=52))
    am_obj.enter_menu(75)
    print_list(am_obj.get_menu(menu_id=75))
    am_obj.play_station('75_7')
    print_songinfo(am_obj)

#    print("Going to play the radio station at hotkey 1.")
#    am_obj.play_hotkey(1)
#    print_songinfo(am_obj)


# ***************************************************************************
#                                    MAIN
# ***************************************************************************
if __name__ == '__main__':
    main()
