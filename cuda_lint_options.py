import os
import shutil
import cudatext as app

KIND_ERROR = 20
KIND_WARN = 21
KIND_INFO = 22

NAME_INI = 'cuda_lint.ini'
ini_app = os.path.join(app.app_path(app.APP_DIR_SETTINGS), NAME_INI)
ini_def = os.path.join(os.path.dirname(__file__), NAME_INI)

if not os.path.isfile(ini_app) and os.path.isfile(ini_def):
    shutil.copyfile(ini_def, ini_app)


def html_color_to_int(s):
    # http://code.activestate.com/recipes/266466-html-colors-tofrom-rgb-tuples/
    """ converts #RRGGBB or #RGB to integers"""
    s = s.strip()
    if not s: return app.COLOR_NONE
    
    while s[0] == '#': s = s[1:]
    # get bytes in reverse order to deal with PIL quirk
    if len(s)==3:
        s = s[0]*2 + s[1]*2 + s[2]*2
    if len(s)!=6:
        raise Exception('Incorrect color token: '+s)
    s = s[-2:] + s[2:4] + s[:2]
    # finally, make it numeric
    color = int(s, 16)
    return color


color_error = html_color_to_int(app.ini_read(ini_app, 'colors', 'error', '#ff00ff'))
color_warn = html_color_to_int(app.ini_read(ini_app, 'colors', 'warn', '#ffff00'))
color_info = html_color_to_int(app.ini_read(ini_app, 'colors', 'info', '#a6caf0'))

use_on_open = app.ini_read(ini_app, 'events', 'on_open', '0')=='1'
use_on_change = app.ini_read(ini_app, 'events', 'on_change', '0')=='1'

fn_warn = os.path.join(os.path.dirname(__file__), 'icons', 'bookmark_warn.bmp')
fn_error = os.path.join(os.path.dirname(__file__), 'icons', 'bookmark_err.bmp')

app.ed.bookmark(app.BOOKMARK_SETUP, 0, KIND_ERROR, color_error, fn_error)
app.ed.bookmark(app.BOOKMARK_SETUP, 0, KIND_WARN, color_warn, fn_warn)
app.ed.bookmark(app.BOOKMARK_SETUP, 0, KIND_INFO, color_info, fn_warn)

def do_register_events():
    ev = []
    if use_on_open: ev+=['on_open']
    if use_on_change: ev+=['on_change_slow']
    if ev:
        ev_list = ','.join(ev)
        print('CudaLint registers events:', ev_list) 
        app.app_proc(app.PROC_SET_EVENTS, 'cuda_lint;' + ev_list+';')
