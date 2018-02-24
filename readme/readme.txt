CudaLint
Command+event plugin for CudaText.
It allows to check/validate syntax of current file, for many lexers. Each lexer must be supported with additionally installed linter:

- JavaScript supported with linter based on JSLint tool,
- HTML supported with linter based on HTML Tidy tool,
- CSS supported with linter based on CSSLint tool,
- etc 

You will find all linters at CudaText's Addon Manager "Install" list. Linters are installable like other plugins but they don't add commands, they only make folders "cuda_lint_nnnnnnn" which are taken by CudaLint later. After you installed a linter, see its readme in its folder, maybe must-read-info here.

=== Node.js ===

Some linters require Node.js and you must install it (with NPM).
Win32: "node.exe" must be in PATH, command "node -v" must work in console.
Linux: "nodejs" package must be installed, command "nodejs -v" must work in console.

=== Usage ===

To call linting, use menu item "Plugins - CudaLint - Lint" or set hotkey to this item (Commands dialog, F9 key). You will see statusbar message, which tells how many errors linter found. For each found error, you'll see yellow or red bookmark on error line (these are unnumbered bookmarks, so use standard commands to work with bookmarks). Plugin also shows list of errors in the "Validate" panel (if found).

Linting can be called by events: on open file, on change text. Events aren't used by default (to not slowdown usual work). To use events, you must enable them in config ("Plugins - CudaLint - Config" menu item).

=== About ===

Authors: Alexey Torgashin, tbeu (http://tbeu.de)

CudaLint uses code portions from the SublimeLinter 3 project.
License: MIT
