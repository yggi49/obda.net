title: 'Simple Local Web Server with Python'
published: 2015-03-06
tags: [python, linux, cheat-sheet]

{% include 'cheat-sheet.md' %}

Python’s standard distribution includes a simple HTTP server, which can be
used to serve a local directory on the fly.  Just open a terminal, change to
the directory you want to share, and run:

    :::bash
    python -m SimpleHTTPServer

Once the server is running, you will see the message:

    Serving HTTP on 0.0.0.0 port 8000 ...

In your browser, you can now access the server by surfing to
[http://localhost:8000](http://localhost:8000).  Moreover, you can also access
the server from other machines in your network, not only from localhost.

If you want to change the server’s port, just provide an additional argument
when launching it:

    :::bash
    python -m SimpleHTTPServer 8888

**Note:** The above solution works only for Python 2, as Python 3 has
reorganized some modules.  If you are working with the latest Python version,
you need to run:

    :::bash
    python -m http.server

or, with a different port:

    :::bash
    python -m http.server 8888
