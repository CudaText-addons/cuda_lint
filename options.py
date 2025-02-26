import os
import cudatext as app

from cudax_lib import get_translation
_   = get_translation(__file__)  # I18N

MY_TAG = 110 #uniq value for all ed.bookmark() plugins

KIND_ERROR = 20
KIND_WARN = 21
KIND_INFO = 22

color_error = 'LightBG1'
color_warn = 'LightBG2'
color_info = 'LightBG3'

color_error_use = True
color_warn_use = True
color_info_use = True

use_on_open = False
use_on_save = False
use_on_change = False

underline = False
underline_style = 6
underline_color = 0xFF0000

fn_ini = os.path.join(app.app_path(app.APP_DIR_SETTINGS), 'cuda_lint.ini')

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
    global underline
    global underline_style

    color_error = app.ini_read(fn_ini, 'colors', 'error_str', color_error)
    color_warn = app.ini_read(fn_ini, 'colors', 'warn_str', color_warn)
    color_info = app.ini_read(fn_ini, 'colors', 'info_str', color_info)

    color_error_use = app.ini_read(fn_ini, 'colors', 'error_use', '1')=='1'
    color_warn_use = app.ini_read(fn_ini, 'colors', 'warn_use', '1')=='1'
    color_info_use = app.ini_read(fn_ini, 'colors', 'info_use', '1')=='1'

    underline = app.ini_read(fn_ini, 'op', 'underline', '0')=='1'
    underline_style = int(app.ini_read(fn_ini, 'op', 'underline_style', '6'))

    use_on_open = app.ini_read(fn_ini, 'events', 'on_open', '0')=='1'
    use_on_save = app.ini_read(fn_ini, 'events', 'on_save', '0')=='1'
    use_on_change = app.ini_read(fn_ini, 'events', 'on_change', '0')=='1'


def do_options_apply():
    global underline_color

    fn_warn = os.path.join(os.path.dirname(__file__), 'icons', 'bookmark_warn.png')
    fn_error = os.path.join(os.path.dirname(__file__), 'icons', 'bookmark_err.png')

    n1 = app.COLOR_NONE
    n2 = app.COLOR_NONE
    n3 = app.COLOR_NONE

    data = app.app_proc(app.PROC_THEME_SYNTAX_DICT_GET, '')

    if color_error in data and color_error_use:
        n1 = data[color_error]['color_back']
    if color_warn in data and color_warn_use:
        n2 = data[color_warn]['color_back']
    if color_info in data and color_info_use:
        n3 = data[color_info]['color_back']

    app.ed.bookmark(app.BOOKMARK_SETUP, 0, KIND_ERROR, n1, fn_error)
    app.ed.bookmark(app.BOOKMARK_SETUP, 0, KIND_WARN, n2, fn_warn)
    app.ed.bookmark(app.BOOKMARK_SETUP, 0, KIND_INFO, n3, fn_warn)

    data_ui = app.app_proc(app.PROC_THEME_UI_DICT_GET, '')
    underline_color = data_ui['EdMicromapSpell']['color']


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
    global underline
    global underline_style

    app.ini_write(fn_ini, 'colors', 'error_str', color_error)
    app.ini_write(fn_ini, 'colors', 'warn_str', color_warn)
    app.ini_write(fn_ini, 'colors', 'info_str', color_info)

    app.ini_write(fn_ini, 'colors', 'error_use', str(int(color_error_use)))
    app.ini_write(fn_ini, 'colors', 'warn_use', str(int(color_warn_use)))
    app.ini_write(fn_ini, 'colors', 'info_use', str(int(color_info_use)))

    app.ini_write(fn_ini, 'op', 'underline', '1' if underline else '0')
    app.ini_write(fn_ini, 'op', 'underline_style', str(underline_style))

    app.ini_write(fn_ini, 'events', 'on_open', str(int(use_on_open)))
    app.ini_write(fn_ini, 'events', 'on_save', str(int(use_on_save)))
    app.ini_write(fn_ini, 'events', 'on_change', str(int(use_on_change)))

    do_options_apply()

do_options_load()
do_options_apply()
