import os
import cudatext as app
from . import options as opt

from cudax_lib import get_translation
_   = get_translation(__file__)  # I18N

p_ini = 'plugins.ini'


def do_options_dlg():

    id_color_err=0
    id_color_warn=2
    id_color_info=4
    id_bk_err=1
    id_bk_warn=3
    id_bk_info=5
    id_ev_open=6
    id_ev_save=7
    id_ev_ch=8
    id_ok=9

    ev_line = app.ini_read(p_ini, 'events', 'cuda_lint', '')
    use_on_open = ',on_open,' in ','+ev_line+','
    use_on_save = ',on_save,' in ','+ev_line+','
    use_on_change = ',on_change_slow,' in ','+ev_line+','

    while True:
        c1 = chr(1)
        text = '\n'.join([]
            +[c1.join(['type=button', 'pos=6,6,180,0', 'cap='+_('Color of &errors')])]
            +[c1.join(['type=check', 'pos=186,6,400,0', 'cap='+_('Colored e&rror bookmarks'), 'val='+str(int(opt.color_error_use))])]
            +[c1.join(['type=button', 'pos=6,36,180,0', 'cap='+_('Color of &warns')])]
            +[c1.join(['type=check', 'pos=186,36,400,0', 'cap='+_('Colored warn &bookmarks'), 'val='+str(int(opt.color_warn_use))])]
            +[c1.join(['type=button', 'pos=6,66,180,0', 'cap='+_('Color of &infos')])]
            +[c1.join(['type=check', 'pos=186,66,400,0', 'cap='+_('Colored info boo&kmarks'), 'val='+str(int(opt.color_info_use))])]
            +[c1.join(['type=check', 'pos=6,100,400,0', 'cap='+_('Lint on &opening file'), 'val='+str(int(use_on_open))])]
            +[c1.join(['type=check', 'pos=6,126,400,0', 'cap='+_('Lint on &saving file'), 'val='+str(int(use_on_save))])]
            +[c1.join(['type=check', 'pos=6,152,400,0', 'cap='+_('Lint &after text changed, and pause'), 'val='+str(int(use_on_change))])]
            +[c1.join(['type=button', 'pos=206,182,300,0', 'cap='+_('OK'), 'props=1'])]
            +[c1.join(['type=button', 'pos=306,182,400,0', 'cap='+_('Cancel')])]
                        )
        res = app.dlg_custom(_('CudaLint options'), 406, 215, text)
        if res is None: return

        btn, text = res

        if btn==id_color_err:
            n=app.dlg_color(opt.color_error)
            if n is not None: opt.color_error=n
            continue

        if btn==id_color_warn:
            n=app.dlg_color(opt.color_warn)
            if n is not None: opt.color_warn=n
            continue

        if btn==id_color_info:
            n=app.dlg_color(opt.color_info)
            if n is not None: opt.color_info=n
            continue

        break

    if btn!=id_ok: return
    text = text.splitlines()

    opt.color_error_use = text[id_bk_err]=='1'
    opt.color_warn_use = text[id_bk_warn]=='1'
    opt.color_info_use = text[id_bk_info]=='1'

    use_on_open = text[id_ev_open]=='1'
    use_on_save = text[id_ev_save]=='1'
    use_on_change = text[id_ev_ch]=='1'

    ev = []
    if use_on_open:
        ev += ['on_open']
    if use_on_save:
        ev += ['on_save']
    if use_on_change:
        ev += ['on_change_slow', 'on_tab_change']
    ev_line_new = ','.join(ev)
    if ev_line!=ev_line_new:
        app.ini_write(p_ini, 'events', 'cuda_lint', ev_line_new)
        app.msg_box(_('CudaText should be restarted, to allow CudaLint use new event-options'), app.MB_OK+app.MB_ICONINFO)

    opt.do_options_save()
    #app.msg_box(_('CudaLint options changed, need to restart app'), app.MB_OK+app.MB_ICONINFO)
