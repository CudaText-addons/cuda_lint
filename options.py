import os
import cudatext as app

MY_TAG = 110 #uniq value for all ed.bookmark() plugins

KIND_ERROR = 20
KIND_WARN = 21
KIND_INFO = 22

color_error = 0
color_warn = 0
color_info = 0

color_error_use = True
color_warn_use = True
color_info_use = True

use_on_open = False
use_on_save = False
use_on_change = False

fn_ini = os.path.join(app.app_path(app.APP_DIR_SETTINGS), 'cuda_lint.ini')

#------------------------
def html_to_int(s):
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

def int_to_html(n):
    s = '%06x' % n
    r, g, b = s[4:], s[2:4], s[:2]
    return '#'+r+g+b
#------------------------

def do_options_load():
    global color_error
    global color_warn
    global color_info
    global color_error_use
    global color_warn_use
    global color_info_use
    global use_on_open
    global use_on_save
    global use_on_change

    color_error = html_to_int(app.ini_read(fn_ini, 'colors', 'error', '#ff00ff'))
    color_warn = html_to_int(app.ini_read(fn_ini, 'colors', 'warn', '#ffff00'))
    color_info = html_to_int(app.ini_read(fn_ini, 'colors', 'info', '#a6caf0'))

    color_error_use = app.ini_read(fn_ini, 'colors', 'error_use', '1')=='1'
    color_warn_use = app.ini_read(fn_ini, 'colors', 'warn_use', '1')=='1'
    color_info_use = app.ini_read(fn_ini, 'colors', 'info_use', '1')=='1'

    use_on_open = app.ini_read(fn_ini, 'events', 'on_open', '0')=='1'
    use_on_save = app.ini_read(fn_ini, 'events', 'on_save', '0')=='1'
    use_on_change = app.ini_read(fn_ini, 'events', 'on_change', '0')=='1'

def do_options_apply():
    fn_warn = os.path.join(os.path.dirname(__file__), 'icons', 'bookmark_warn.png')
    fn_error = os.path.join(os.path.dirname(__file__), 'icons', 'bookmark_err.png')

    app.ed.bookmark(app.BOOKMARK_SETUP, 0, KIND_ERROR, color_error if color_error_use else app.COLOR_NONE, fn_error)
    app.ed.bookmark(app.BOOKMARK_SETUP, 0, KIND_WARN, color_warn if color_warn_use else app.COLOR_NONE, fn_warn)
    app.ed.bookmark(app.BOOKMARK_SETUP, 0, KIND_INFO, color_info if color_info_use else app.COLOR_NONE, fn_warn)

def do_options_save():
    global color_error
    global color_warn
    global color_info
    global color_error_use
    global color_warn_use
    global color_info_use
    global use_on_open
    global use_on_save
    global use_on_change

    app.ini_write(fn_ini, 'colors', 'error', int_to_html(color_error))
    app.ini_write(fn_ini, 'colors', 'warn', int_to_html(color_warn))
    app.ini_write(fn_ini, 'colors', 'info', int_to_html(color_info))

    app.ini_write(fn_ini, 'colors', 'error_use', str(int(color_error_use)))
    app.ini_write(fn_ini, 'colors', 'warn_use', str(int(color_warn_use)))
    app.ini_write(fn_ini, 'colors', 'info_use', str(int(color_info_use)))

    app.ini_write(fn_ini, 'events', 'on_open', str(int(use_on_open)))
    app.ini_write(fn_ini, 'events', 'on_save', str(int(use_on_save)))
    app.ini_write(fn_ini, 'events', 'on_change', str(int(use_on_change)))

    do_options_apply()

do_options_load()
do_options_apply()
