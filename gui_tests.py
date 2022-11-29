import PySimpleGUI as sg
import logging
import types

# FIXME RENAME! Name collides with other lib!!!
import tests

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
    
    line = [sg.Button("PLAY", key=('searchplay', s['id']), enable_events=True)]
    line += [sg.Button("+", key=('add_fav', s['id']), enable_events=True,
               button_color=('white', 'springgreen4'))]
    line += [sg.T(s['name'])]
    return line

# Init
am = tests.api_init(IPADDR, TIMEOUT)
favs = tests.get_favs(am)

# Window init
try:
    favs = [fav_to_line(f) for f in favs]
except KeyError:
    favs = [sg.T('BRAK')]
col_favs = [sg.Column(favs, scrollable=True, vertical_scroll_only=True, k='colfavs')]

search_line = [sg.Button('SZUKAJ', key='search', enable_events=True),
                 sg.Input('', key='search_text')]

search_results_col = [sg.Column([], scrollable=True, vertical_scroll_only=True, k='colsearchres')]

vol_lines = [sg.Button('Mute', key='mute', enable_events=True),
             sg.T('Volume: ', size=(6,1)),
             #sg.Button('SET', key='vol_set', enable_events=True),
             sg.Slider(range=(0,30),
                       default_value=tests.get_vol(am=am),
                       size=(20,15),
                       orientation='horizontal',
                       font=('Helvetica', 12),
                       key='vol_set',
                       disable_number_display=False,
                       enable_events=True,
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
def _play():
    pass

@register_event
def play(values):
    pass

@register_event
def del_fav(values):
    pass

@register_event
def add_fav(values):
    pass

@register_event
def search(values):
    search_results_raw = tests.search_stations(name=values['search_text'])
    logging.debug(f"Search results raw: {search_results_raw}")
    search_results = [search_res_line(s) for s in search_results_raw]
    logging.debug(f"Search results: {search_results}")
    window.extend_layout(window['colsearchres'], search_results)
    window.refresh()
    window['colsearchres'].contents_changed()

@register_event
def search_play(values):
    pass

@register_event
def mute(values):
    pass

@register_event
def vol_set(values):
    pass


while True:
    event, values = window.Read()
    logging.debug((event, values))
    
    if event is None or event == 'Exit':
        break
    
    registered_events[event](values)
