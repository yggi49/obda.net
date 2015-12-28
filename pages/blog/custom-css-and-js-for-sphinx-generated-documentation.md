title: 'Custom CSS and JS for Sphinx-Generated Documentation'
published: 2015-12-28
tags: [sphinx, css, javascript]

When generating HTML documentation with [Sphinx][1], it is possible to adjust
a couple of theme-related settings by defining `html_theme_options` in your
`conf.py`, e.g.:

    :::python
    html_theme_options = {
        'rightsidebar': True,
        'textcolor': '#333',
    }

However, the available options that can be customized are (a) rather
restricted, and (b) specific to each theme.  The `[options]` section of a
theme’s `theme.conf` sheds light on what can be done (and what not).

On a global basis, though, you can define `html_context` to add some custom
CSS and JavaScript files:

    :::python
    html_context = {
        'css_files': ['_static/custom.css'],
        'script_files': ['_static/custom.js'],
    }

The files listed there will be included last in the generated HTML files’
sources, so it is easy to directly tweak the generated documentation’s final
appearance (and, if needed, behavior).

For reference, have a look at Sphinx’s
`builders.html.StandaloneHTMLBuilder.prepare_writing()` and see
[how `self.globalcontext` gets populated there][2].


[1]: http://sphinx-doc.org/
[2]: https://github.com/sphinx-doc/sphinx/blob/master/sphinx/builders/html.py#L327
