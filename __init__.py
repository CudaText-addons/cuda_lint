import sys
import os
import cudatext
import cudatext_cmd

sys.path.append(os.path.dirname(__file__))
from SublimeLinter.lint.linter import linter_classes

from . import cuda_lint_options

class Command:
    def __init__(self):
        dir = cudatext.app_path(cudatext.APP_DIR_PY)
        dirs = os.listdir(dir)
        dirs = [name for name in dirs if name.startswith('cuda_lint_') and os.path.isdir(os.path.join(dir, name))]
        for lint in dirs:
            try:
                __import__(lint + '.linter', globals(), locals(), [lint + '.linter'])
            except ImportError:
                pass

    def do_lint(self, editor, show_panel=False):
        lexer = editor.get_prop(cudatext.PROP_LEXER_FILE)
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
                            #cudatext.ed.focus()
                            cudatext.ed.cmd(cudatext_cmd.cmd_ShowPanelValidate)
                            cudatext.ed.focus()
                        cudatext.msg_status('Linter "%s" found %d error(s)' % (linter.name, error_count))
                    else:
                        if show_panel:
                            cudatext.msg_status('Linter "%s" found no errors' % linter.name)
                    return
        else:
            if show_panel:
                cudatext.msg_status('No linters installed for "%s"' % lexer)

    def on_open(self, ed_self):
        self.do_lint(ed_self)

    def on_save(self, ed_self):
        self.do_lint(ed_self)

    def on_change_slow(self, ed_self):
        self.do_lint(ed_self)

    def run(self):
        self.do_lint(cudatext.ed, True)

    def on_start(self, ed_self):
        cuda_lint_options.do_register_events()
        
    def config(self):
        cudatext.file_open(cuda_lint_options.ini_app)
