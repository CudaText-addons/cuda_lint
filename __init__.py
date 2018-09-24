import sys
import os
import cudatext as app
import cudatext_cmd as cmds

from .linter import Linter, linter_classes
from .python_linter import PythonLinter
from . import options
from . import dialogs


def get_project_linter(lexer):
    '''Gets linter module name, from lexer name'''
    if not lexer: return

    try:
        import cuda_project_man
    except ImportError:
        print('CudaLint cannot import cuda_project_man')
        return

    v = cuda_project_man.project_variables()
    if v:
        return v.get('linter_'+lexer.lower())


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
        proj_linter = get_project_linter(lexer)

        for linterName in linter_classes:
            Linter = linter_classes[linterName]

            if isinstance(Linter.syntax, (tuple, list)):
                match = lexer in Linter.syntax
            else:
                match = lexer == Linter.syntax

            if match and proj_linter:
                dir = Linter.__module__.split('.')[0] #was 'cuda_lint_nnn.linter'
                prefix = 'cuda_lint_'
                if dir.startswith(prefix):
                    dir = dir[len(prefix):]
                #print('Checking linter:', dir)
                match = dir==proj_linter

            if match:
                if not Linter.disabled:
                    linter = Linter(editor)
                    error_count = linter.lint()
                    if error_count > 0:
                        if show_panel:
                            app.ed.cmd(cmds.cmd_ShowPanelValidate)
                            app.ed.focus()
                        app.msg_status('Linter "%s" found %d error(s)' % (linter.name, error_count))
                    else:
                        if show_panel:
                            app.msg_status('Linter "%s" found no errors' % linter.name)
                    return
        else:
            self.clear_valid_pan()
            if show_panel:
                if proj_linter:
                    s = 'Project\'s required linter not found: %s' % proj_linter
                else:
                    s = 'No linters for lexer "%s"' % lexer
                app.msg_status(s)

    def on_open(self, ed_self):
        if options.use_on_open:
            self.do_lint(ed_self)

    def on_save(self, ed_self):
        if options.use_on_save:
            self.do_lint(ed_self)

    def on_change_slow(self, ed_self):
        if options.use_on_change:
            self.do_lint(ed_self)

    def on_tab_change(self, ed_self):
        if options.use_on_change:
            self.do_lint(ed_self)

    def run(self):
        self.do_lint(app.ed, True)

    def run_goto(self):
        self.run()
        items = app.ed.bookmark(app.BOOKMARK_GET_LIST, 0)
        if items:
            app.ed.set_caret(0, items[0])

    def config(self):
        dialogs.do_options_dlg()

    def clear_valid_pan(self):
        app.app_log(app.LOG_CLEAR, '', panel=app.LOG_PANEL_VALIDATE)

    def disable(self):
        self.en = False
        app.msg_status('CudaLint disabled')

        # clear bookmarks
        for h in app.ed_handles():
            e = app.Editor(h)
            e.bookmark(app.BOOKMARK_CLEAR_ALL, 0)
        self.clear_valid_pan()

    def enable(self):
        self.en = True
        app.msg_status('CudaLint enabled')

