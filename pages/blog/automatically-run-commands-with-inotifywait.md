title: 'Automatically Run Commands with inotifywait'
published: 2014-08-25
updated: 2015-12-19
tags: [linux, cheat-sheet, inotify]

{% include 'cheat-sheet.md' %}

You can use inotifywait from [inotify-tools][1] to automatically run commands,
for example whenever a file is written to.

The following shell loop runs `xelatex` whenever `~/input.tex` changes:

    :::bash
    inotifywait -m -e close_write ~/input.tex | while read line
    do
        xelatex -interaction nonstopmode ~/input.tex
    done

It is also possible to watch more than one file.  Additionally, if using the
`-r` switch, any specified directory will be watched recursively:

    :::bash
    inotifywait -m -e close_write -r locale/ | while read line
    do
        python manage.py compilemessages
    done

### Update: December 19, 2015

The previous version of this article did not make use of inotifywait’s `-m`
option:

    :::bash
    while inotifywait -e close_write -r locale/
    do
        python manage.py compilemessages
    done

This way, inotify’s watches are re-setup after each single run of the
specified command.  If watching large directory trees, this is a pretty
expensive operation.

In contrast, the `-m` option activates inotifywait’s “monitor” mode—the
necessary watches are set up only once, and inotifywait runs indefinitely.

[1]: http://freecode.com/projects/inotify-tools
