title: 'Zsh History Expansion'
published: 2014-05-28
tags: [zsh, cheat-sheet]

{% include 'cheat-sheet.md' %}

Shortcut | Description
- | -
`!!` | the entire previous command
`!!^` | the first *argument* from the previous command
`!!*` | all *arguments* from the previous command
`!!:`*`n`* | the *`n`*-th *word* from the previous command
`!!$` | the last *word* from the previous command
`!#` | the entire current command line (typed in so far)
`!#^` | the first *argument* from the current command line
`!#*` | all *arguments* from the current command line
`!#:`*`n`* | the *`n`*-th *word* from the current command line
`!#$` | the last *word* from the current command line

For more information, read [Andrew Grangaard][1]’s [Zsh history expansion][2]
article.

[1]: https://www.blogger.com/profile/14818383405782029025
[2]: http://www.lowlevelmanager.com/2012/05/zsh-history-expansion.html
