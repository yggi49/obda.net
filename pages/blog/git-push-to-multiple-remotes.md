title: git push to Multiple Remotes
published: 2016-06-28
tags: [git]
refs:
    - '[Git - Pushing code to two
      remotes](http://stackoverflow.com/a/14290145/192916) (Stack Overflow)'

If you happen to have two remotes for your git repository—e.g. one at GitHub
and one on a private server—you might want to `git push` your changes to both
remotes at once.

To achieve this, you can leverage Git’s ability to have multiple push URLs for
a remote.  Create a new remote, e.g. named `all`, and set both remotes’ URLs
as push URLs:

    git remote add all <remote_url1>
    git remote set-url all --add --push <remote_url1>
    git remote set-url all --add --push <remote_url2>

Pushing the master branch to both remotes is now as easy as running:

    git push all master

Note: of course you could just set both remote URLs as push URLs for `origin`.
However, by creating a new remote for this purpose, you can still push to any
remote separately if you want.
