# coding=utf8
#
# util.py
# Part of SublimeLinter3, a code checking framework for Sublime Text 3
#
# Written by Ryan Hileman and Aparajita Fishman
#
# Project: https://github.com/SublimeLinter/SublimeLinter3
# License: MIT
#

#
# Public constants
#

import os
import re
import sys
from threading import Timer
import shutil
import subprocess
import tempfile
import platform
from numbers import Number

#
# Public constants
#
STREAM_STDOUT = 1
STREAM_STDERR = 2
STREAM_BOTH = STREAM_STDOUT + STREAM_STDERR

PYTHON_CMD_RE = re.compile(r'(?P<script>[^@]+)?@python(?P<version>[\d\.]+)?')
VERSION_RE = re.compile(r'(?P<major>\d+)(?:\.(?P<minor>\d+))?')

INLINE_SETTINGS_RE = re.compile(r'(?i).*?\[sublimelinter[ ]+(?P<settings>[^\]]+)\]')
INLINE_SETTING_RE = re.compile(r'(?P<key>[@\w][\w\-]*)\s*:\s*(?P<value>[^\s]+)')

MENU_INDENT_RE = re.compile(r'^(\s+)\$menus', re.MULTILINE)

MARK_COLOR_RE = (
    r'(\s*<string>sublimelinter\.{}</string>\s*\r?\n'
    r'\s*<key>settings</key>\s*\r?\n'
    r'\s*<dict>\s*\r?\n'
    r'\s*<key>foreground</key>\s*\r?\n'
    r'\s*<string>)#.+?(</string>\s*\r?\n)'
)

ANSI_COLOR_RE = re.compile(r'\033\[[0-9;]*m')


def can_exec(path):
    """Return whether the given path is a file and is executable."""
    return os.path.isfile(path) and os.access(path, os.X_OK)

def convert_type(value, type_value, sep=None, default=None):
    """
    Convert value to the type of type_value.

    If the value cannot be converted to the desired type, default is returned.
    If sep is not None, strings are split by sep (plus surrounding whitespace)
    to make lists/tuples, and tuples/lists are joined by sep to make strings.

    """

    if type_value is None or isinstance(value, type(type_value)):
        return value

    if isinstance(value, str):
        if isinstance(type_value, (tuple, list)):
            if sep is None:
                return [value]
            else:
                if value:
                    return re.split(r'\s*{}\s*'.format(sep), value)
                else:
                    return []
        elif isinstance(type_value, Number):
            return float(value)
        else:
            return default

    if isinstance(value, Number):
        if isinstance(type_value, str):
            return str(value)
        elif isinstance(type_value, (tuple, list)):
            return [value]
        else:
            return default

    if isinstance(value, (tuple, list)):
        if isinstance(type_value, str):
            return sep.join(value)
        else:
            return list(value)

    return default

def which(cmd, module=None):
    """
    Return the full path to the given command, or None if not found.

    If cmd is in the form [script]@python[version], find_python is
    called to locate the appropriate version of python. The result
    is a tuple of the full python path and the full path to the script
    (or None if there is no script).

    """

    match = PYTHON_CMD_RE.match(cmd)

    if match:
        args = match.groupdict()
        args['module'] = module
        if module is not None:
            path = '<builtin>'
            script_path = os.path.join(os.path.dirname(module.__file__), args['script'] + '.py')
            available_version = {
                'major': sys.version_info.major,
                'minor': sys.version_info.minor
            }
            result = (path, script_path, available_version['major'], available_version['minor'])
            return result
        else:
            print('ERROR: not yet implemented.')
            return ''
    else:
        return find_executable(cmd)

def find_executable(executable):
    """
    Return the path to the given executable, or None if not found.

    create_environment is used to augment PATH before searching
    for the executable.

    """

    env = create_environment()
    path_list = env.get('PATH', '').split(os.pathsep)

    for base in path_list:
        path = os.path.join(os.path.expanduser(base), executable)

        # On Windows, if path does not have an extension, try .exe, .cmd, .bat
        if os.name=='nt' and not os.path.splitext(path)[1]:
            for extension in ('.exe', '.cmd', '.bat'):
                path_ext = path + extension

                if can_exec(path_ext):
                    return path_ext
        elif can_exec(path):
            return path

    return None


def touch(path):
    """Perform the equivalent of touch on Posix systems."""
    with open(path, 'a'):
        os.utime(path, None)


def open_directory(path):
    """Open the directory at the given path in a new window."""

    cmd = (get_subl_executable_path(), path)
    subprocess.Popen(cmd, cwd=path)

def run_shell_cmd(cmd, output_stream = STREAM_STDOUT):
    '''Run a shell command and return stdout.'''
    proc = popen(cmd, output_stream, env = create_environment())
    if proc is not None:
        timeout = {'value': False}
        timer = Timer(10, kill_proc, [proc, timeout])
        timer.start()
        out = proc.communicate()
        timer.cancel()
        return combine_output(out)
    else:
        return ''

def kill_proc(proc, timeout):
    print('shell timed out after {} seconds, executing {}'.format(10, cmd))
    timeout['value'] = True
    proc.kill()

def create_environment():
    """
    Return a dict with os.environ augmented with a better PATH.

    On Posix systems, the user's shell PATH is added to PATH.

    Platforms paths are then added to PATH by getting the
    "paths" user settings for the current platform. If "paths"
    has a "*" item, it is added to PATH on all platforms.

    """

    env = {}
    env.update(os.environ)

    # Many linters use stdin, and we convert text to utf-8
    # before sending to stdin, so we have to make sure stdin
    # in the target executable is looking for utf-8.
    env['PYTHONIOENCODING'] = 'utf8'

    # Trick from "Tern for Sublime" plugin, needed for macOS
    if platform.system() == "Darwin":
        env["PATH"] += ":/usr/local/bin"

    return env

# popen utils

def combine_output(out, sep=''):
    """Return stdout and/or stderr combined into a string, stripped of ANSI colors."""
    output = sep.join((
        (out[0].decode('utf8') or '') if out[0] else '',
        (out[1].decode('utf8') or '') if out[1] else '',
    ))

    return ANSI_COLOR_RE.sub('', output)


def communicate(cmd, code='', output_stream=STREAM_STDOUT, env=None):
    """
    Return the result of sending code via stdin to an executable.

    The result is a string which comes from stdout, stderr or the
    combining of the two, depending on the value of output_stream.
    If env is not None, it is merged with the result of create_environment.

    """

    out = popen(cmd, output_stream=output_stream, extra_env=env)

    if out is not None:
        code = code.encode('utf8')
        out = out.communicate(code)
        return combine_output(out)
    else:
        return ''


def tmpfile(cmd, code, suffix='', output_stream=STREAM_STDOUT, env=None):
    """
    Return the result of running an executable against a temporary file containing code.

    It is assumed that the executable launched by cmd can take one more argument
    which is a filename to process.

    The result is a string combination of stdout and stderr.
    If env is not None, it is merged with the result of create_environment.

    """

    f = None

    try:
        with tempfile.NamedTemporaryFile(suffix=suffix, prefix='_CudaLint_', delete=False) as f:
            if isinstance(code, str):
                code = code.encode('utf-8')

            f.write(code)
            f.flush()

        cmd = list(cmd)

        if '@' in cmd:
            cmd[cmd.index('@')] = f.name
        else:
            cmd.append(f.name)

        out = popen(cmd, output_stream=output_stream, extra_env=env)

        if out:
            out = out.communicate()
            return combine_output(out)
        else:
            return ''
    finally:
        if f:
            os.remove(f.name)


def tmpdir(cmd, files, filename, code, output_stream=STREAM_STDOUT, env=None):
    """
    Run an executable against a temporary file containing code.

    It is assumed that the executable launched by cmd can take one more argument
    which is a filename to process.

    Returns a string combination of stdout and stderr.
    If env is not None, it is merged with the result of create_environment.

    """

    filename = os.path.basename(filename)
    d = tempfile.mkdtemp()
    out = None

    try:
        for f in files:
            try:
                os.makedirs(os.path.join(d, os.path.dirname(f)))
            except OSError:
                pass

            target = os.path.join(d, f)

            if os.path.basename(target) == filename:
                # source file hasn't been saved since change, so update it from our live buffer
                f = open(target, 'wb')

                if isinstance(code, str):
                    code = code.encode('utf8')

                f.write(code)
                f.close()
            else:
                shutil.copyfile(f, target)

        os.chdir(d)
        out = popen(cmd, output_stream=output_stream, extra_env=env)

        if out:
            out = out.communicate()
            out = combine_output(out, sep='\n')

            # filter results from build to just this filename
            # no guarantee all syntaxes are as nice about this as Go
            # may need to improve later or just defer to communicate()
            out = '\n'.join([
                line for line in out.split('\n') if filename in line.split(':', 1)[0]
            ])
        else:
            out = ''
    finally:
        shutil.rmtree(d, True)

    return out or ''


def popen(cmd, output_stream=STREAM_BOTH, env=None, extra_env=None):
    """Open a pipe to an external process and return a Popen object."""
    info = None

    try:
        from subprocess import DEVNULL # py3k
    except ImportError:
        DEVNULL = open(os.devnull, 'wb')

    if os.name == 'nt':
        info = subprocess.STARTUPINFO()
        info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        info.wShowWindow = subprocess.SW_HIDE

    if output_stream == STREAM_BOTH:
        stdout = stderr = subprocess.PIPE
    elif output_stream == STREAM_STDOUT:
        stdout = subprocess.PIPE
        stderr = DEVNULL
    else:  # STREAM_STDERR
        stdout = DEVNULL
        stderr = subprocess.PIPE

    if env is None:
        env = create_environment()

    if extra_env is not None:
        env.update(extra_env)

    try:
        return subprocess.Popen(
            cmd, stdin=subprocess.PIPE,
            stdout=stdout, stderr=stderr,
            startupinfo=info, env=env)
    except Exception as err:
        print(err)
