title: 'Redirect STDIN in a Shell Script'
published: 2014-06-10
tags: [zsh, cheat-sheet]

{% include 'cheat-sheet.md' %}

If you have a shell script, and want to redirect all input it receives via
STDIN to another script or program, use `<&0`:

    :::sh
    #!/bin/zsh
    /path/to/another/script.pl --script-args <&0
