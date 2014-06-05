title: 'Zsh Line Editor Shortcuts'
published: 2014-05-27
tags: [zsh, cheat-sheet]

{% include 'cheat-sheet.md' %}

*__Note:__ These shortcuts are valid for Zsh’s `emacs` mode, not necessarily
for `vi` mode.*

Shortcut | Description
- | -
`M-.` | insert the last word from the previous history entry[^b140527a]
`C-u` | kill the current line
`C-v C-j` | insert newline at current cursor position
`C-x C-e` | edit current command line in `$EDITOR`
`C-x C-f` *`char`* | move to the next occurrence of character *`char`*

[^b140527a]:
    press `M-.` repeatedly to get the last words from older history entries
