title: 'Convert Filenames Recursively to Lower Case'
published: 2014-08-11
tags: [zsh, cheat-sheet]

{% include 'cheat-sheet.md' %}

Use `zmv` to recursively convert the names of all files and (sub-) directories
within the current directory to lower case:

    :::bash
    autoload zmv
    zmv '(**/)(*)' '$1${2:l}'

If you want to convert to upper case instead of lower case, use `:u` instead
of `:l`.
