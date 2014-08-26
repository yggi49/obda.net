title: 'Automatically Run Commands with inotifywait'
published: 2014-08-25
tags: [linux, cheat-sheet, inotify]

{% include 'cheat-sheet.md' %}

You can use inotifywait from [inotify-tools][1] to automatically run commands,
for example whenever a file is written to.

The following shell loop runs `xelatex` whenever `~/input.tex` changes:

    :::bash
    while inotifywait -e close_write ~/input.tex
    do
        xelatex -interaction nonstopmode ~/input.tex
    done

It is also possible to watch more than one file.  Additionally, if using the
`-r` switch, any specified directory will be watched recursively:

    :::bash
    while inotifywait -e close_write -r ~/my/django/project/locale/
    do
        python manage.py compilemessages
    done

[1]: http://freecode.com/projects/inotify-tools
