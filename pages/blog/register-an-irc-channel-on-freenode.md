title: 'Register an IRC Channel on freenode'
published: 2014-05-12
tags: [irc, freenode]

First, register your nickname if you haven’t done so yet:

    :::text
    /msg NickServ REGISTER my_password my.email.address@example.com

Login (“identify”) with *NickServ*:

    :::text
    /msg NickServ IDENTIFY my_nick my_password

Next, register your channel:

    :::text
    /msg ChanServ REGISTER #my-channel

Change the channel’s topic:

    :::text
    /msg ChanServ TOPIC #my-channel my_topic

If the channel is not very frequented, you might want to set the `KEEPTOPIC`
flag.  Otherwise, you have to re-set the topic every time:

    :::text
    /msg ChanServ SET #my-channel KEEPTOPIC ON

Hide information about the channel from other users:

    :::text
    /msg ChanServ SET #my-channel PRIVATE ON

Restrict the channel to user’s who are on the channel’s access list:

    :::text
    /msg ChanServ SET #my-channel RESTRICTED ON

Add and remove users to the access list—only registered user accounts are
allowed:

    :::text
    /msg ChanServ ACCESS #my-channel ADD other_user
    /msg ChanServ ACCESS #my-channel DEL bugging_user

Display access list:

    :::text
    /msg ChanServ ACCESS #my-channel LIST
