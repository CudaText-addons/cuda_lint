CudaLint (plugin for CudaText).
It allows to check/validate syntax of current file, for many lexers. Each lexer must be supported
with additionally installed linter, for example:

- JavaScript is supported with linter based on JSLint tool,
- HTML is supported with linter based on HTML Tidy tool,
- CSS is supported with linter based on CSSLint tool,
- etc

You will find all linters in the Addon Manager: "Plugins / Addon Manager / Install".
Linters are installable like other plugins but they don't add commands, they only add folders
"py/cuda_lint_*", which are automatically used by CudaLint.
After you install a linter, see readme in its folder, maybe how-to-use info is written there.


Node.js
-------

Some linters require Node.js, so for those linters, you must install Node first.
Those linters are sometimes shipped with Node modules preinstalled (in plugin folder)
and sometimes you need to install Node modules via NPM.
See linter's readme file for details.

Windows: "node.exe" must be in PATH, command "node -v" must work in console.
Linux: "node" (preferred) or "nodejs" package must be installed.
At least on Ubuntu, "nodejs" is older than "node" (2025/02 on Ubuntu 22.04:
"nodejs" is 12.x, while "node" is 22.x).


Usage
-----

To run linting, use menu item "Plugins / CudaLint / Lint", or set hotkey to this command
(in CudaText Command Palette, press F9). You will see statusbar message, which tells how many errors
linter found. For each found error, you'll see yellow/red bookmark (you can use usual commands
for these bookmarks). Plugin also shows list of errors in the "Validate" panel
(to show Validate panel, click V icon on the CudaText sidebar).

Linting can be run by events:
- after opening file
- before saving file
- after text is changed + pause passed

Events aren't used by default (to not slowdown usual work). To use events, you must enable them in config.
Call config by menu item in "Options / Settings-plugins".



How to configure linters per project
------------------------------------

In your project (Project Manager plugin), right-click root node of project treeview, call menu item
"Project file / Project properties...". In this dialog, in the "Variablies" field, enter variable(s) like this:

linter_css=csslint

Variable prefix "linter_" is required, after goes lower-case lexer name (CSS).
Value of variable must be name of linter's folder (in the "py" folder) without "cuda_lint_".
So if linter's folder is py/cuda_lint_aaa, specify the value "aaa".

In this example, CudaLint plugin allows, for mentioned lexer CSS, only linter "csslint",
even if another CSS linter (e.g. "csstree") is installed and found first.


About
-----

Authors:
- Alexey Torgashin (CudaText)
- TBeu, http://tbeu.de

CudaLint uses code portions from the SublimeLinter 3 project.
License: MIT
