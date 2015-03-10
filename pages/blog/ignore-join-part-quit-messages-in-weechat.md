title: 'Ignore join/part/quit messages in WeeChat'
published: 2015-03-10
tags: [irc, weechat, cheat-sheet]

{% include 'cheat-sheet.md' %}

From the [WeeChat FAQ][1]:

> With smart filter (keep join/part/quit from users who spoke recently):
>
>     /set irc.look.smart_filter on
>     /filter add irc_smart * irc_smart_filter *
>
> With a global filter (hide all join/part/quit):
>
>     /filter add joinquit * irc_join,irc_part,irc_quit *

Ignoring the messages only in specific channels can be achieved by providing
the full channel names (in a comma-separated list) after the filter name:

    /filter add myfilter irc.freenode.#mychannel irc_smart_filter *

Use `/filter disable myfilter` or `/filter del myfilter` to disable or delete
the filter.

[1]: https://weechat.org/files/doc/weechat_faq.en.html#filter_irc_join_part_quit
