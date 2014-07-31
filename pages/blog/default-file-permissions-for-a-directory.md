title: 'Default File Permissions for a Directory'
published: 2014-07-31
tags: [linux, posix-acls, cheat-sheet]

{% include 'cheat-sheet.md' %}

You can set the default permissions for all files created in a given directory
using POSIX access control lists (ACLs).  For example, after executing

    :::console
    user@host:~$ setfacl -d -m u::rwx,g::rwx,o::r-x ~/path/to/example/dir

all new files (and directories, too) in `~/path/to/example/dir` will have
group write permission enabled.  To check the currently effective ACLs, use
`getfacl`.
