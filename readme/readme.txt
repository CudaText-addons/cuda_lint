CudaLint (plugin for CudaText).
It allows to check/validate syntax of current file, for many lexers. Each lexer must be supported
with additionally installed linter, for example:

- JavaScript is supported with linter based on JSLint tool,
- HTML is supported with linter based on HTML Tidy tool,
- CSS is supported with linter based on CSSLint tool,
- etc

You will find all linters in the Addon Manager: "Plugins / Addon Manager / Install".
Linters are installable like other plugins but they don't add commands, they only add folders
"[CudaText]/py/cuda_lint_*", which are automatically used by CudaLint.
After you install a linter, see readme in its folder, maybe how-to-use info is written there.

=== Node.js ===

Some linters require Node.js, so for those linters, you must install Node first.
Those linters are sometimes shipped with Node modules preinstalled (in plugin folder)
and sometimes you need to install Node modules via NPM.
See linter's readme file for details.

Windows: "node.exe" must be in PATH, command "node -v" must work in console.
Linux: "nodejs" package must be installed, command "nodejs -v" must work in terminal.

=== Usage ===

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

=== About ===

Authors:
- Alexey Torgashin (CudaText)
- TBeu, http://tbeu.de

CudaLint uses code portions from the SublimeLinter 3 project.
License: MIT
