import PySimpleGUI as sg
import logging
import types

# FIXME RENAME! Name collides with other lib!!!
import tests

sg.theme('Dark Blue 3') 

IPADDR = 'azradio.lan'
TIMEOUT = 5
#logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.DEBUG)

registered_events = {}

def register_event(e):
    global registered_events
    
    if e.__name__ in registered_events:
        logging.warning(f"Handler already registered: {e.__name__}")
    registered_events[e.__name__] = e
    
    return e


def fav_to_line(f):
    if not ('id' in f) and not ('name' in f):
        logging.error("Can't create fav line: {f}")
        return [sg.T("Error")]
    
    line = [sg.Button("PLAY", key=('play', f['id']), enable_events=True)]
    line += [sg.Button("X", key=('del_fav', f['id']), enable_events=True,
               button_color=('white', 'firebrick3'))]
    line += [sg.T(f['name'])]
    return line

def search_res_line(s):
    if not ('id' in s) and not ('name' in s):
        logging.error("Can't create search line: {s}")
        return [sg.T("Error")]
    
    line = [sg.Button("PLAY", key=('search_play', s['id']), enable_events=True)]
    line += [sg.Button("+", key=('add_fav', s['id']), enable_events=True,
               button_color=('white', 'springgreen4'))]
    line += [sg.T(s['name'])]
    return line

def get_favs():
    favs = tests.get_favs(am)
    try:
        favs = [fav_to_line(f) for f in favs]
    except KeyError:
        favs = [sg.T('BRAK')]
    
    return favs

# Init
am = tests.api_init(IPADDR, TIMEOUT)
favs = get_favs()

# Window init
col_favs = [sg.Column(favs, scrollable=True, vertical_scroll_only=True, 
                      expand_x=True, expand_y=True, k='colfavs')]

search_line = [sg.Button('SZUKAJ', key='search', enable_events=True, expand_x=True),
                 sg.Input('', key='search_text')]

search_results_col = [sg.Column([], scrollable=True, vertical_scroll_only=True,
                                expand_x=True, expand_y=True, k='colsearchres')]

vol_lines = [sg.Button('Wycisz', key='mute', enable_events=True),
             sg.T('Głośność: '),
             #sg.Button('SET', key='vol_set', enable_events=True),
             sg.Slider(range=(0,30),
                       default_value=tests.get_vol(am=am),
                       size=(20,15),
                       orientation='horizontal',
                       font=('Helvetica', 12),
                       key='vol_set',
                       disable_number_display=False,
                       enable_events=True,
                       expand_x=True,
                       tooltip='Głośność'),
            ]

layout = [ [sg.T('Ulubione:')],
           col_favs,
           [sg.HorizontalSeparator()],
           [sg.T('Wyszukaj:')],
           search_line,
           search_results_col,
           [sg.HorizontalSeparator()],
           vol_lines,
         ]

WINDOW_TITLE = 'Panel sterowania radiem'
window = sg.Window(WINDOW_TITLE, layout, resizable=True)

del(am) # Free, events will re-init it when needed
am = None

#
def _play(values):
    tests.play_station(station_id=values['event_key_args'])

@register_event
def play(values):
    logging.debug(f"Play! Values: {values}")
    _play(values)

def update_col(key, new_elements):
    global window
    # FIXME Unable to clear the Column Element before adding new items here!
    logging.debug(window[key].Rows)
    #for widget in window[key].Widget.winfo_children():
    #        widget.destroy()
    window.extend_layout(window[key], new_elements)
    window[key].contents_changed()
    window.refresh()

def refresh_favs():
    favs = get_favs()
    update_col('colfavs', favs)

@register_event
def del_fav(values):
    pass

@register_event
def add_fav(values):
    logging.debug(f"Add fav! Values: {values}")
    # FIXME Station isn't favved
    tests.set_fav(station_id=values['event_key_args'])
    refresh_favs()

@register_event
def search(values):
    search_results = []
    if values['search_text']:
        search_results_raw = tests.search_stations(name=values['search_text'])
        logging.debug(f"Search results raw: {search_results_raw}")
        search_results = [search_res_line(s) for s in search_results_raw]
    logging.debug(f"Search results: {search_results}")
    update_col('colsearchres', search_results)

@register_event
def search_play(values):
    logging.debug(f"Search_play! Values: {values}")
    _play(values)

@register_event
def mute(values):
    mute = tests.get_mute()
    # Negate the mute:
    return tests.set_mute(mute=(not mute))

@register_event
def vol_set(values):
    # Use window.perform_long_operation() to not to freeze GUI for the time of
    # the call execution?
    tests.set_vol(v=values['vol_set'])
    

while True:
    event_tup, values = window.Read()
    logging.debug((event_tup, values))
    
    if isinstance(event_tup, tuple):
        event, event_key_args = event_tup
    else:
        event = event_tup
        event_key_args = ""
    
    if event is None or event == 'Exit' or event == sg.WIN_CLOSED:
        break
    
    # Copy station id from part of button's key tuple to event key args
    values['event_key_args'] = event_key_args
    
    logging.debug((event, values))
    try:
        registered_events[event](values)
    except Exception as e:
        sg.popup_error_with_traceback('Error on event', 'Something went wrong', e)
