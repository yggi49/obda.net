title: 'Tweaking Gentoo’s Greeting Message'
published: 2015-12-29
tags: [linux, gentoo]

{% include 'gentoo-disclaimer.md' %}

Gentoo’s standard greeting message on the console looks like this:

    This is <my_hostname>.<my_domain> (Linux x86_64 4.3.3-gentoo) 12:00:00

While informative, it isn’t really pretty.  Modifying it turns out to be quite
easy, though: just edit `/etc/issue`!  By default, it contains:

    This is \n.\O (\s \m \r) \t

Simply adjust this to your needs, and you are done.  Especially removing `.\O`
might be of interest, as this gets rid of the ugly `.unknown_domain` part
which you get in case you don’t have a domain configured.
