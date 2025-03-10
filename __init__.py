import sys
import os
import cudatext as app
import cudatext_cmd as cmds

from cudax_lib import get_translation
_   = get_translation(__file__)  # I18N

from .linter import Linter, linter_classes
from .python_linter import PythonLinter
from . import options
from . import dialogs


def get_project_linter(lexer):
    if not lexer: return

    try:
        import cuda_project_man
    except ImportError:
        print(_('CudaLint cannot import cuda_project_man'))
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

        avail = []
        for (linterName, Linter) in linter_classes.items():

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
                    avail.append((linterName, Linter))

        self.clear_valid_pan()

        if avail:
            if len(avail) == 1:
                Linter = avail[0][1]
            else:
                res = app.dlg_menu(app.DMENU_LIST, [i[0] for i in avail], caption=_('Linters for %s') % lexer)
                if res is None: return
                Linter = avail[res][1]

            linter = Linter(editor)
            error_count = linter.lint()
            if error_count > 0:
                if show_panel:
                    editor.cmd(cmds.cmd_ShowPanelValidate)
                    editor.focus()
                app.msg_status(_('Linter "{}" found {} error(s)').format(linter.name, error_count))
            else:
                if show_panel:
                    app.msg_status(_('Linter "%s" found no errors') % linter.name)
        else:
            if show_panel:
                if proj_linter:
                    s = _('Project\'s required linter not found: %s') % proj_linter
                else:
                    s = _('No linters for lexer "%s"') % lexer
                app.msg_status(s)


    def on_open(self, ed_self):
        self.do_lint(ed_self)

    def on_save(self, ed_self):
        self.do_lint(ed_self)

    def on_change_slow(self, ed_self):
        self.do_lint(ed_self)

    def on_tab_change(self, ed_self):
        self.do_lint(ed_self)

    def run(self):
        self.en = True
        self.do_lint(app.ed, True)

    def run_goto(self):
        self.run()
        items = app.ed.bookmark(app.BOOKMARK_GET_ALL, 0)
        if items:
            for item in items:
                if item['tag']==options.MY_TAG:
                    app.ed.set_caret(0, item['line'])

    def config(self):
        dialogs.do_options_dlg()

    def clear_valid_pan(self):
        app.app_log(app.LOG_CLEAR, '', panel=app.LOG_PANEL_VALIDATE)

    def disable(self):
        self.en = False
        app.msg_status(_('CudaLint disabled'))

        # clear bookmarks
        for h in app.ed_handles():
            e = app.Editor(h)
            e.attr(app.MARKERS_DELETE_BY_TAG, tag=options.MY_TAG)
            e.bookmark(app.BOOKMARK_DELETE_BY_TAG, 0, tag=options.MY_TAG)
        self.clear_valid_pan()

    def enable(self):
        self.en = True
        app.msg_status(_('CudaLint enabled'))

