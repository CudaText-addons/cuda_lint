import os
import cudatext as app
from . import options as opt

from cudax_lib import get_translation
_   = get_translation(__file__)  # I18N

p_ini = 'plugins.ini'

COLORS = [
    'LightBG1',
    'LightBG2',
    'LightBG3',
    'LightBG4',
    'LightBG5',
    'IncludeBG1',
    'IncludeBG2',
    'IncludeBG3',
    'IncludeBG4',
    'SectionBG1',
    'SectionBG2',
    'SectionBG3',
    'SectionBG4',
    'CurBlockBG',
    'SeparLine',
    ]

UNDERLINE_STYLES = [
    _('None'),
    _('Solid'),
    _('Dash'),
    _('Solid 2px'),
    _('Dotted'),
    _('Rounded'),
    _('Wave'),
    ]

def do_options_dlg():

    ID_COLOR_ERR      = 0
    ID_COLOR_WARN     = 2
    ID_COLOR_INFO     = 4
    ID_BK_ERR         = 1
    ID_BK_WARN        = 3
    ID_BK_INFO        = 5
    ID_UNDERLINE      = 6
    ID_UNDERLINE_STYLE= 7
    ID_EV_OPEN        = 8
    ID_EV_SAVE        = 9
    ID_EV_CH          = 10
    ID_OK             = 11

    ev_line = app.ini_read(p_ini, 'events', 'cuda_lint', '')
    use_on_open = ',on_open,' in ','+ev_line+','
    use_on_save = ',on_save,' in ','+ev_line+','
    use_on_change = ',on_change_slow,' in ','+ev_line+','
    
    try:
        val_er = COLORS.index(opt.color_error)
    except ValueError:
        val_er = 0

    try:
        val_warn = COLORS.index(opt.color_warn)
    except ValueError:
        val_warn = 0

    try:
        val_info = COLORS.index(opt.color_info)
    except ValueError:
        val_info = 0

    while True:
        c1 = chr(1)
        text = '\n'.join([]
            +[c1.join(['type=combo_ro', 'pos=6,6,180,26', 'items='+'\t'.join(COLORS), 'val='+str(val_er) ])]
            +[c1.join(['type=check', 'pos=186,6,400,0', 'cap='+_('Colored e&rror bookmarks'), 'val='+str(int(opt.color_error_use))])]
            +[c1.join(['type=combo_ro', 'pos=6,36,180,56', 'items='+'\t'.join(COLORS), 'val='+str(val_warn) ])]
            +[c1.join(['type=check', 'pos=186,36,400,0', 'cap='+_('Colored warn &bookmarks'), 'val='+str(int(opt.color_warn_use))])]
            +[c1.join(['type=combo_ro', 'pos=6,66,180,86', 'items='+'\t'.join(COLORS), 'val='+str(val_info) ])]
            +[c1.join(['type=check', 'pos=186,66,400,0', 'cap='+_('Colored info boo&kmarks'), 'val='+str(int(opt.color_info_use))])]
            +[c1.join(['type=check', 'pos=6,100,400,0', 'cap='+_('Underline errors, don\'t place bookmarks'), 'val='+str(int(opt.underline))])]
            +[c1.join(['type=combo_ro', 'pos=6,130,180,0', 'items='+'\t'.join(UNDERLINE_STYLES), 'val='+str(opt.underline_style)])]
            +[c1.join(['type=check', 'pos=6,170,400,0', 'cap='+_('Lint on &opening file'), 'val='+str(int(use_on_open))])]
            +[c1.join(['type=check', 'pos=6,190,400,0', 'cap='+_('Lint on &saving file'), 'val='+str(int(use_on_save))])]
            +[c1.join(['type=check', 'pos=6,210,400,0', 'cap='+_('Lint &after text changed, and pause'), 'val='+str(int(use_on_change))])]
            +[c1.join(['type=button', 'pos=206,242,300,0', 'cap='+_('OK'), 'ex0=1'])]
            +[c1.join(['type=button', 'pos=306,242,400,0', 'cap='+_('Cancel')])]
                        )
        res = app.dlg_custom(_('CudaLint options'), 406, 275, text)
        if res is None: return

        btn, text = res
        break

    if btn!=ID_OK: return
    text = text.splitlines()

    opt.color_error = COLORS[int(text[ID_COLOR_ERR])]
    opt.color_warn = COLORS[int(text[ID_COLOR_WARN])]
    opt.color_info = COLORS[int(text[ID_COLOR_INFO])]

    opt.color_error_use = text[ID_BK_ERR]=='1'
    opt.color_warn_use = text[ID_BK_WARN]=='1'
    opt.color_info_use = text[ID_BK_INFO]=='1'

    opt.underline = text[ID_UNDERLINE]=='1'
    opt.underline_style = int(text[ID_UNDERLINE_STYLE])
    
    use_on_open = text[ID_EV_OPEN]=='1'
    use_on_save = text[ID_EV_SAVE]=='1'
    use_on_change = text[ID_EV_CH]=='1'

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
