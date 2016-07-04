import cudatext as app
from . import options as opt

def do_options_dlg():
    id_color_err=0
    id_color_warn=2
    id_color_info=4
    id_bk_err=1
    id_bk_warn=3
    id_bk_info=5
    id_ev_open=6
    id_ev_ch=7
    id_ok=8

    while True:
        c1 = chr(1)
        text = '\n'.join([] 
            +[c1.join(['type=button', 'pos=6,6,180,0', 'cap=Color of &errors'])]
            +[c1.join(['type=check', 'pos=186,6,400,0', 'cap=Colored e&rror bookmarks', 'val='+str(int(opt.color_error_use))])]
            +[c1.join(['type=button', 'pos=6,36,180,0', 'cap=Color of &warns'])]
            +[c1.join(['type=check', 'pos=186,36,400,0', 'cap=Colored warn &bookmarks', 'val='+str(int(opt.color_warn_use))])]
            +[c1.join(['type=button', 'pos=6,66,180,0', 'cap=Color of &infos'])]
            +[c1.join(['type=check', 'pos=186,66,400,0', 'cap=Colored info boo&kmarks', 'val='+str(int(opt.color_info_use))])]
            +[c1.join(['type=check', 'pos=6,100,400,0', 'cap=Do linting on &opening file', 'val='+str(int(opt.use_on_open))])]
            +[c1.join(['type=check', 'pos=6,126,400,0', 'cap=Do linting &after text changed', 'val='+str(int(opt.use_on_change))])]
            +[c1.join(['type=button', 'pos=206,156,300,0', 'cap=OK', 'props=1'])]
            +[c1.join(['type=button', 'pos=306,156,400,0', 'cap=Cancel'])]
            )
        res = app.dlg_custom('CudaLint options', 406, 190, text)
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
    
    opt.use_on_open = text[id_ev_open]=='1'
    opt.use_on_change = text[id_ev_ch]=='1'
    
    opt.do_options_save()
    app.msg_box('CudaLint options changed, need to restart app', app.MB_OK+app.MB_ICONINFO)
    