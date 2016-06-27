import sys
import os
import cudatext as app
import cudatext_cmd as cmds

sys.path.append(os.path.dirname(__file__))
from SublimeLinter.lint.linter import linter_classes

import cuda_lint_options as opt
import cuda_lint_opt_dialog as dlg

def do_register_events():
    ev = []
    if opt.use_on_open: ev+=['on_open']
    if opt.use_on_change: ev+=['on_change_slow']
    if ev:
        ev_list = ','.join(ev)
        print('CudaLint registers events:', ev_list) 
        app.app_proc(app.PROC_SET_EVENTS, 'cuda_lint;' + ev_list+';')


class Command:
    def __init__(self):
        dir = app.app_path(app.APP_DIR_PY)
        dirs = os.listdir(dir)
        dirs = [name for name in dirs if name.startswith('cuda_lint_') and os.path.isdir(os.path.join(dir, name))]
        for lint in dirs:
            try:
                __import__(lint + '.linter', globals(), locals(), [lint + '.linter'])
            except ImportError:
                pass

    def do_lint(self, editor, show_panel=False):
        lexer = editor.get_prop(app.PROP_LEXER_FILE)
        for linterName in linter_classes:
            Linter = linter_classes[linterName]

            if isinstance(Linter.syntax, (tuple, list)):
                match = lexer in Linter.syntax
            else:
                match = lexer == Linter.syntax

            if match:
                if not Linter.disabled:
                    linter = Linter(editor)
                    error_count = linter.lint()
                    if error_count > 0:
                        if show_panel:
                            #app.ed.focus()
                            app.ed.cmd(cmds.cmd_ShowPanelValidate)
                            app.ed.focus()
                        app.msg_status('Linter "%s" found %d error(s)' % (linter.name, error_count))
                    else:
                        if show_panel:
                            app.msg_status('Linter "%s" found no errors' % linter.name)
                    return
        else:
            if show_panel:
                app.msg_status('No linters installed for "%s"' % lexer)

    def on_open(self, ed_self):
        self.do_lint(ed_self)

    def on_save(self, ed_self):
        self.do_lint(ed_self)

    def on_change_slow(self, ed_self):
        self.do_lint(ed_self)

    def run(self):
        self.do_lint(app.ed, True)

    def on_start(self, ed_self):
        do_register_events()
        
    def config(self):
        dlg.do_options_dlg()
        
