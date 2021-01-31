# coding=utf-8
#
# linter.py
# Part of SublimeLinter3, a code checking framework for Sublime Text 3
#
# Written by Ryan Hileman and Aparajita Fishman
# Change for CudaLint: Alexey T.
#
# Project: https://github.com/SublimeLinter/SublimeLinter3
# License: MIT
#

import os
import re
import shlex
from numbers import Number

import cudatext as app
from . import util
from .options import KIND_ERROR, KIND_WARN, KIND_INFO, MY_TAG

from cudax_lib import get_translation
_   = get_translation(__file__)  # I18N

WARNING = 'warning'
ERROR = 'error'

#
# Private constants
#
ARG_RE = re.compile(r'(?P<prefix>@|--?)?(?P<name>[@\w][\w\-]*)(?:(?P<joiner>[=:])(?:(?P<sep>.)(?P<multiple>\+)?)?)?')

# Colors of bookmarks

linter_classes = {}

class LinterMeta(type):

    def __init__(cls, name, bases, attrs):
        """
        Initialize a Linter class.

        When a Linter subclass is loaded by Sublime Text, this method is called.
        We take this opportunity to do some transformations:

        - Compile regex patterns.
        - Convert strings to tuples where necessary.
        - Add a leading dot to the tempfile_suffix if necessary.
        - Build a map between defaults and linter arguments.
        - Add '@python' as an inline setting to PythonLinter subclasses.

        Finally, the class is registered as a linter for its configured syntax.

        """

        if bases:
            setattr(cls, 'disabled', False)

            if name in ('PythonLinter', 'RubyLinter'):
                return

            cmd = attrs.get('cmd')

            if isinstance(cmd, str):
                setattr(cls, 'cmd', shlex.split(cmd))

            syntax = attrs.get('syntax')

            try:
                if isinstance(syntax, str) and syntax[0] == '^':
                    setattr(cls, 'syntax', re.compile(syntax))
            except re.error as err:
                print(
                    _('ERROR: {} disabled, error compiling syntax: {}')
                    .format(name.lower(), str(err))
                )
                setattr(cls, 'disabled', True)

            if not cls.disabled:
                for regex in ('regex', 'comment_re', 'word_re', 'version_re'):
                    attr = getattr(cls, regex)

                    if isinstance(attr, str):
                        if regex == 'regex' and cls.multiline:
                            setattr(cls, 're_flags', cls.re_flags | re.MULTILINE)

                        try:
                            setattr(cls, regex, re.compile(attr, cls.re_flags))
                        except re.error as err:
                            print(
                                _('ERROR: {} disabled, error compiling {}: {}')
                                .format(name.lower(), regex, str(err))
                            )
                            setattr(cls, 'disabled', True)

            if not cls.disabled:
                if not cls.syntax or (cls.cmd is not None and not cls.cmd) or not cls.regex:
                    print(_('ERROR: {} disabled, not fully implemented').format(name.lower()))
                    setattr(cls, 'disabled', True)

            for attr in ('inline_settings', 'inline_overrides'):
                if attr in attrs and isinstance(attrs[attr], str):
                    setattr(cls, attr, (attrs[attr],))

            cls.reinitialize()

            global linter_classes
            linter_classes[name] = cls

class Linter(metaclass=LinterMeta):

    """
    The base class for linters.

    Subclasses must at a minimum define the attributes syntax, cmd, and regex.

    """

    #
    # Public attributes
    #

    # The syntax that the linter handles. May be a string or
    # list/tuple of strings. Names should be all lowercase.
    syntax = ''

    # A string, list, tuple or callable that returns a string, list or tuple, containing the
    # command line (with arguments) used to lint.
    cmd = ''

    # If the name of the executable cannot be determined by the first element of cmd
    # (for example when cmd is a method that dynamically generates the command line arguments),
    # this can be set to the name of the executable used to do linting.
    #
    # Once the executable's name is determined, its existence is checked in the user's path.
    # If it is not available, the linter is disabled.
    executable = None

    # If the executable is available, this is set to the full path of the executable.
    # If the executable is not available, it is set an empty string.
    # Subclasses should consider this read only.
    executable_path = None

    # Some linter plugins have version requirements as far as the linter executable.
    # The following three attributes can be defined to define the requirements.
    # version_args is a string/list/tuple that represents the args used to get
    # the linter executable's version as a string.
    version_args = None

    # A regex pattern or compiled regex used to match the numeric portion of the version
    # from the output of version_args. It must contain a named capture group called
    # "version" that captures only the version, including dots but excluding a prefix
    # such as "v".
    version_re = None

    # A string which describes the version requirements, suitable for passing to
    # the distutils.versionpredicate.VersionPredicate constructor, as documented here:
    # http://pydoc.org/2.5.1/distutils.versionpredicate.html
    # Only the version requirements (what is inside the parens) should be
    # specified here, do not include the package name or parens.
    version_requirement = None

    # A regex pattern used to extract information from the executable's output.
    regex = ''

    # Set to True if the linter outputs multiline error messages. When True,
    # regex will be created with the re.MULTILINE flag. Do NOT rely on setting
    # the re.MULTILINE flag within the regex yourself, this attribute must be set.
    multiline = False

    # If you want to set flags on the regex *other* than re.MULTILINE, set this.
    re_flags = 0

    # The default type assigned to non-classified errors. Should be either
    # ERROR or WARNING.
    default_type = WARNING

    # Linters usually report errors with a line number, some with a column number
    # as well. In general, most linters report one-based line numbers and column
    # numbers. If a linter uses zero-based line numbers or column numbers, the
    # linter class should define this attribute accordingly.
    line_col_base = (0, 0)

    # If the linter executable cannot receive from stdin and requires a temp file,
    # set this attribute to the suffix of the temp file (with or without leading '.').
    # If the suffix needs to be mapped to the syntax of a file, you may make this
    # a dict that maps syntax names (all lowercase, as used in the syntax attribute),
    # to tempfile suffixes. The syntax used to lookup the suffix is the mapped
    # syntax, after using "syntax_map" in settings. If the view's syntax is not
    # in this map, the class' syntax will be used.
    #
    # Some linters can only work from an actual disk file, because they
    # rely on an entire directory structure that cannot be realistically be copied
    # to a temp directory (e.g. javac). In such cases, set this attribute to '-',
    # which marks the linter as "file-only". That will disable the linter for
    # any views that are dirty.
    tempfile_suffix = None

    # Linters may output to both stdout and stderr. By default stdout and sterr are captured.
    # If a linter will never output anything useful on a stream (including when
    # there is an error within the linter), you can ignore that stream by setting
    # this attribute to the other stream.
    error_stream = util.STREAM_BOTH

    # Many linters look for a config file in the linted file?s directory and in
    # all parent directories up to the root directory. However, some of them
    # will not do this if receiving input from stdin, and others use temp files,
    # so looking in the temp file directory doesn?t work. If this attribute
    # is set to a tuple of a config file argument and the name of the config file,
    # the linter will automatically try to find the config file, and if it is found,
    # add the config file argument to the executed command.
    #
    # Example: config_file = ('--config', '.jshintrc')
    #
    config_file = None

    # Tab width
    tab_width = 1

    # If a linter can be used with embedded code, you need to tell SublimeLinter
    # which portions of the source code contain the embedded code by specifying
    # the embedded scope selectors. This attribute maps syntax names
    # to embedded scope selectors.
    #
    # For example, the HTML syntax uses the scope `source.js.embedded.html`
    # for embedded JavaScript. To allow a JavaScript linter to lint that embedded
    # JavaScript, you would set this attribute to {'html': 'source.js.embedded.html'}.
    selectors = {}

    # If a linter reports a column position, SublimeLinter highlights the nearest
    # word at that point. You can customize the regex used to highlight words
    # by setting this to a pattern string or a compiled regex.
    word_re = None

    # If you want to provide default settings for the linter, set this attribute.
    # If a setting will be passed as an argument to the linter executable,
    # you may specify the format of the argument here and the setting will
    # automatically be passed as an argument to the executable. The format
    # specification is as follows:
    #
    # <prefix><name><joiner>[<sep>[+]]
    #
    # - <prefix>: Either empty, '@', '-' or '--'.
    # - <name>: The name of the setting.
    # - <joiner>: Either '=' or ':'. If <prefix> is empty or '@', <joiner> is ignored.
    #   Otherwise, if '=', the setting value is joined with <name> by '=' and
    #   passed as a single argument. If ':', <name> and the value are passed
    #   as separate arguments.
    # - <sep>: If the argument accepts a list of values, <sep> specifies
    #   the character used to delimit the list (usually ',').
    # - +: If the setting can be a list of values, but each value must be
    #   passed as a separate argument, terminate the setting with '+'.
    #
    # After the format is parsed, the prefix and suffix are removed and the
    # setting is replaced with <name>.
    defaults = None

    # Linters may define a list of settings that can be specified inline.
    # As with defaults, you can specify that an inline setting should be passed
    # as an argument by using a prefix and optional suffix. However, if
    # the same setting was already specified as an argument in defaults,
    # you do not need to use the prefix or suffix here.
    #
    # Within a file, the actual inline setting name is '<linter>-setting', where <linter>
    # is the lowercase name of the linter class.
    inline_settings = None

    # Many linters allow a list of options to be specified for a single setting.
    # For example, you can often specify a list of errors to ignore.
    # This attribute is like inline_settings, but inline values will override
    # existing values instead of replacing them, using the override_options method.
    inline_overrides = None

    # If the linter supports inline settings, you need to specify the regex that
    # begins a comment. comment_re should be an unanchored pattern (no ^)
    # that matches everything through the comment prefix, including leading whitespace.
    #
    # For example, to specify JavaScript comments, you would use the pattern:
    #    r'\s*/[/*]'
    # and for python:
    #    r'\s*#'
    comment_re = None

    # Some linters may want to turn a shebang into an inline setting.
    # To do so, set this attribute to a callback which receives the first line
    # of code and returns a tuple/list which contains the name and value for the
    # inline setting, or None if there is no match.
    shebang_match = None

    #
    # Internal class storage, do not set
    #
    env = None
    disabled = False
    executable_version = None

    @classmethod
    def initialize(cls):
        """
        Perform class-level initialization.

        If subclasses override this, they should call super().initialize() first.

        """
        pass

    @classmethod
    def reinitialize(cls):
        """
        Perform class-level initialization after plugins have been loaded at startup.

        This occurs if a new linter plugin is added or reloaded after startup.
        Subclasses may override this to provide custom behavior, then they must
        call cls.initialize().

        """
        cls.initialize()

    def __init__(self, view):
        self.view = view
        self.code = ''

    @property
    def filename(self):
        """Return the view's file path or '' of unsaved."""
        return self.view.get_filename()

    @property
    def name(self):
        """Return the class name lowercased."""
        return self.__class__.__name__.lower()

    def find_errors(self, output):
        """
        A generator which matches the linter's regex against the linter output.

        If multiline is True, split_match is called for each non-overlapping
        match of self.regex. If False, split_match is called for each line
        in output.

        """

        if self.multiline:
            errors = self.regex.finditer(output)

            if errors:
                for error in errors:
                    yield self.split_match(error)
            else:
                yield self.split_match(None)
        else:
            for line in output.splitlines():
                yield self.split_match(self.regex.match(line.rstrip()))

    def split_match(self, match):
        """
        Split a match into the standard elements of an error and return them.

        If subclasses need to modify the values returned by the regex, they
        should override this method, call super(), then modify the values
        and return them.

        """

        if match:
            items = {'line': None, 'col': None, 'error': None, 'warning': None, 'message': '', 'near': None}
            items.update(match.groupdict())
            line, col, error, warning, message, near = [
                items[k] for k in ('line', 'col', 'error', 'warning', 'message', 'near')
            ]

            if line is not None:
                line = int(line) - self.line_col_base[0]

            if col is not None:
                if col.isdigit():
                    col = int(col) - self.line_col_base[1]
                else:
                    col = len(col) + 1

            return match, line, col, error, warning, message, near
        else:
            return match, None, None, None, None, '', None


    def get_cmd(self):
        """
        Calculate and return a tuple/list of the command line to be executed.

        The cmd class attribute may be a string, a tuple/list, or a callable.
        If cmd is callable, it is called. If the result of the method is
        a string, it is parsed into a list with shlex.split.

        Otherwise the result of build_cmd is returned.

        """
        if callable(self.cmd):
            cmd = self.cmd()

            if isinstance(cmd, str):
                cmd = shlex.split(cmd)

            return self.insert_args(cmd)
        else:
            return self.build_cmd()

    def build_cmd(self, cmd=None):
        """
        Return a tuple with the command line to execute.

        We start with cmd or the cmd class attribute. If it is a string,
        it is parsed with shlex.split.

        If the first element of the command line matches [script]@python[version],
        and '@python' is in the aggregated view settings, util.which is called
        to determine the path to the script and given version of python. This
        allows settings to override the version of python used.

        Otherwise, if self.executable_path has already been calculated, that
        is used. If not, the executable path is located with util.which.

        If the path to the executable can be determined, a list of extra arguments
        is built with build_args. If the cmd contains '*', it is replaced
        with the extra argument list, otherwise the extra args are appended to
        cmd.

        """

        cmd = cmd or self.cmd
        if cmd is None: return

        if isinstance(cmd, str):
            cmd = shlex.split(cmd)
        else:
            cmd = list(cmd)

        which = cmd[0]
        have_path, path = self.context_sensitive_executable_path(cmd)

        if have_path:
            # Returning None means the linter runs code internally
            if path == '<builtin>':
                return None
        elif self.executable_path:
            path = self.executable_path

            if isinstance(path, (list, tuple)) and None in path:
                path = None
        else:
            path = self.which(which)

        if not path:
            persist.printf(_('ERROR: {} cannot locate \'{}\'').format(self.name, which))
            return ''

        cmd[0:1] = util.convert_type(path, [])
        return self.insert_args(cmd)

    def context_sensitive_executable_path(self, cmd):
        """
        Calculate the context-sensitive executable path, return a tuple of (have_path, path).

        Subclasses may override this to return a special path.

        """
        return False, None

    def lint(self):
        """
        Perform the lint, retrieve the results, and add marks to the view.

        The flow of control is as follows:

        - Get the command line. If it is an empty string, bail.
        - Run the linter.
        - If the view has been modified since the original hit_time, stop.
        - Parse the linter output with the regex.
        - Highlight warnings and errors.

        """

        error_count = 0

        if self.filename:
            cwd = os.getcwd()
            os.chdir(os.path.dirname(self.filename))

        if self.cmd is None:
            cmd = None
        else:
            settings = {}
            args_map = {}
            if not self.defaults is None:
                for name, value in self.defaults.items():
                    match = ARG_RE.match(name)

                    if match:
                        name = match.group('name')
                        args_map[name] = match.groupdict()

                    settings[name] = value

            args = list()
            for setting, arg_info in args_map.items():
                prefix = arg_info['prefix']

                if setting not in settings or setting[0] == '@' or prefix is None:
                    continue

                values = settings[setting]

                if values is None:
                    continue
                elif isinstance(values, (list, tuple)):
                    if values:
                        # If the values can be passed as a single list, join them now
                        if arg_info['sep'] and not arg_info['multiple']:
                            values = [str(value) for value in values]
                            values = [arg_info['sep'].join(values)]
                    else:
                        continue
                elif isinstance(values, str):
                    if values:
                        values = [values]
                    else:
                        continue
                elif isinstance(values, Number):
                    if values is False:
                        continue
                    else:
                        values = [values]
                else:
                    # Unknown type
                    continue

                for value in values:
                    if prefix == '@':
                        args.append(str(value))
                    else:
                        arg = prefix + arg_info['name']
                        joiner = arg_info['joiner']

                        if joiner == '=':
                            args.append('{}={}'.format(arg, value))
                        elif joiner == ':':
                            args.append(arg)
                            args.append(str(value))

            if callable(self.cmd):
                cmd = self.cmd()
            else:
                cmd = self.cmd
            if isinstance(cmd, str):
                cmd = shlex.split(cmd)
            else:
                cmd = list(cmd)

            which = cmd[0]
            have_path, path = self.context_sensitive_executable_path(cmd)

            if have_path:
                # Returning None means the linter runs code internally
                if path == '<builtin>':
                    return 0
            elif which is None or self.executable_path is None:
                executable = ''

                if not callable(self.cmd):
                    if isinstance(self.cmd, (tuple, list)):
                        executable = (self.cmd or [''])[0]
                    elif isinstance(self.cmd, str):
                        executable = self.cmd

                if not executable and self.executable:
                    executable = self.executable

                if executable:
                    path = util.which(executable) or ''

                    if (
                        path is None or
                        (isinstance(path, (tuple, list)) and None in path)
                    ):
                        path = ''
                else:
                    path = None
            elif self.executable_path:
                path = self.executable_path

                if isinstance(path, (list, tuple)) and None in path:
                    path = None
            else:
                path = util.which(which)

            if not path:
                print(_('ERROR: {} cannot locate "{}"').format(self.name, which))
                return 0

            cmd[0:1] = util.convert_type(path, [])

            if '*' in cmd:
                i = cmd.index('*')

                if args:
                    cmd[i:i + 1] = args
                else:
                    cmd.pop(i)
            else:
                cmd += args

            if cmd is not None and not cmd:
                return 0

        output = self.run(cmd, self.view.get_text_all())

        self.view.bookmark(app.BOOKMARK_DELETE_BY_TAG, 0, tag=MY_TAG)
        if not output:
            return 0

        if self.filename:
            os.chdir(cwd)

        app.app_log(app.LOG_CLEAR, '', panel=app.LOG_PANEL_VALIDATE)
        app.app_log(app.LOG_SET_FILENAME, self.filename, panel=app.LOG_PANEL_VALIDATE)
        app.app_log(app.LOG_SET_LINE_ID, '1', panel=app.LOG_PANEL_VALIDATE)
        app.app_log(app.LOG_SET_COL_ID, '2', panel=app.LOG_PANEL_VALIDATE)
        app.app_log(app.LOG_SET_ZEROBASE, '0', panel=app.LOG_PANEL_VALIDATE)
        app.app_log(app.LOG_SET_REGEX, 'Line (\d+) Col (\d+):.+', panel=app.LOG_PANEL_VALIDATE)

        m = []
        error_list = self.find_errors(output)
        for match, line, col, error, warning, message, near in error_list:
            if match and message and line is not None:
                m.append((line, col, message, error, warning))

        error_count = 0
        if m:
            m = sorted(m, key = lambda m: m[0])
            bm = dict()
            for line, col, message, error, warning in m:
                if error:
                    bm_kind = KIND_ERROR
                elif warning:
                    bm_kind = KIND_WARN
                else:
                    if self.default_type == ERROR:
                        bm_kind = KIND_ERROR
                    elif self.default_type == WARNING:
                        bm_kind = KIND_WARN
                    else:
                        bm_kind = KIND_INFO

                if col is None:
                    col = 1
                app.app_log(app.LOG_ADD,
                            'Line {} Col {}: {}'.format(line, col, message),
                            panel=app.LOG_PANEL_VALIDATE)

                bm[line] = (line-1, bm_kind, message)
                error_count += 1

            self.view.bookmark(app.BOOKMARK_DELETE_BY_TAG, 0, tag=MY_TAG)
            for line in bm:
                self.view.bookmark(app.BOOKMARK_SET, 
                    nline=bm[line][0], 
                    nkind=bm[line][1], 
                    text=bm[line][2],
                    tag=MY_TAG,
                    show=False
                    )

        return error_count


    def run(self, cmd, code):
        """
        Execute the linter's executable or built in code and return its output.

        If a linter uses built in code, it should override this method and return
        a string as the output.

        If a linter needs to do complicated setup or will use the tmpdir
        method, it will need to override this method.

        """

        if self.tempfile_suffix:
            if self.tempfile_suffix != '-':
                return self.tmpfile(cmd, code, suffix=self.get_tempfile_suffix())
            else:
                return self.communicate(cmd)
        else:
            return self.communicate(cmd, code)

    def get_tempfile_suffix(self):
        """Return the mapped tempfile_suffix."""
        if self.tempfile_suffix:
            if not isinstance(self.tempfile_suffix, dict):
                suffix = self.tempfile_suffix

            if suffix and suffix[0] != '.':
                suffix = '.' + suffix

            return suffix
        else:
            return ''

    # popen wrappers

    def communicate(self, cmd, code=''):
        """Run an external executable using stdin to pass code and return its output."""
        if '@' in cmd:
            cmd[cmd.index('@')] = self.filename
        elif not code:
            cmd.append(self.filename)

        res = util.communicate(
            cmd,
            code,
            output_stream=self.error_stream,
            env=self.env)
        #print('Communucate result-')
        #print(res)
        return res

    def tmpfile(self, cmd, code, suffix=''):
        """Run an external executable using a temp file to pass code and return its output."""
        return util.tmpfile(
            cmd,
            code,
            suffix or self.get_tempfile_suffix(),
            output_stream=self.error_stream,
            env=self.env)

    def tmpdir(self, cmd, files, code):
        """Run an external executable using a temp dir filled with files and return its output."""
        return util.tmpdir(
            cmd,
            files,
            self.filename,
            code,
            output_stream=self.error_stream,
            env=self.env)

    def popen(self, cmd, env=None):
        """Run cmd in a subprocess with the given environment and return the output."""
        return util.popen(
            cmd,
            env=env,
            extra_env=self.env,
            output_stream=self.error_stream)
