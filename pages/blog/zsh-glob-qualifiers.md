title: 'Zsh Glob Qualifiers'
published: 2014-05-02
tags: [zsh, cheat-sheet]

{% include 'cheat-sheet.md' %}

### Examples

    :::bash
    # three newest (by mtime) files
    print *(.om[1,3])
    # files larger than 50 kiB
    print *(.Lk+50)
    # files modified within the last hour
    print *(.mh-1)
    # files not accessed for six months or longer
    print *(.aM+6)
    # change ownership of anything that is owned by `alice` to `bob`
    chown bob **/*(u:alice:)


### Full List

Qualifier | Description
- | -
`/` | directory
`F` | non-empty directory (empty: `(/^F)`)
`.` | plain file
`@` | symbolic link
`*` | executable plain file
`r`/`A`/`R` | readable by owner/group/world
`w`/`I`/`W` | writable by owner/group/world
`x`/`E`/`X` | executable by owner/group/world
`s`/`S`/`t` | setuid/setgid/sticky bit
`f`*`spec`* | has `chmod` style permissions *`spec`*
`u:`*`name`*`:` | owned by user *`name`*
`g:`*`name`*`:` | owned by group *`name`*
`a[Mwhms][-+]`*`n`* | access time in given units (see below)
`m[Mwhms][-+]`*`n`* | modification time in given units
`L[kmp][-+]`*`n`* | size in given units (see below)
`^` | negate following qualifiers
`-` | toggle following links (first one turns on)
`N` | whole pattern expands to empty if no match
`D` | leading dots may be matched
`n` | sort numbers numerically
`o[nLamd]` | order by given code (see below; may repeat)
`O[nLamd]` | order by reverse of given code
`[`*`num`*`]` | select *`num`*-th file in current order
`[`*`num1`*`,`*`num2`*`]` | select *`num1`*-th to *`num2`*-th file

  * **Time units:** Month, week, hour, minute, second; default: day.
  * **Size units:** kilobytes, megabytes; default: bytes
  * **Order codes:** name (default), size, atime, mtime, directory depth
