import sys
import os
import cudatext as app
import cudatext_cmd as cmds

from .linter import Linter, linter_classes
from .python_linter import PythonLinter
from . import options
from . import dialogs


class Command:
    en = True
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
        if not self.en:
            return
            
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
        if options.use_on_open:
            self.do_lint(ed_self)

    def on_save(self, ed_self):
        if options.use_on_save:
            self.do_lint(ed_self)

    def on_change_slow(self, ed_self):
        if options.use_on_change:
            self.do_lint(ed_self)

    def run(self):
        self.do_lint(app.ed, True)

    def config(self):
        dialogs.do_options_dlg()
        

    def disable(self):
        self.en = False
        app.msg_status('CudaLint disabled')
        
        #clear bookmarks
        for h in app.ed_handles():
            e = app.Editor(h)
            e.bookmark(app.BOOKMARK_CLEAR_ALL, 0)
            e.bookmark(app.BOOKMARK_CLEAR_HINTS, 0)
            
        #clear Valid pane
        app.app_log(app.LOG_SET_PANEL, app.LOG_PANEL_VALIDATE)
        app.app_log(app.LOG_CLEAR, '')
        

    def enable(self):
        self.en = True
        app.msg_status('CudaLint enabled')
