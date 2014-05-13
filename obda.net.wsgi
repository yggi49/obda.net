#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import Counter
import datetime
import math
import sys

from flask import (Flask, render_template, render_template_string, url_for,
                   abort, request, redirect)
from flask_flatpages import FlatPages, pygments_style_defs, pygmented_markdown
from markupsafe import Markup


# Configuration
# =============

pages = FlatPages()

class DefaultConfig(object):

    @staticmethod
    def prerender_jinja(text):
        prerendered_body = render_template_string(Markup(text))
        return pygmented_markdown(prerendered_body, pages)

    DEBUG = False
    FLATPAGES_AUTO_RELOAD = False
    FLATPAGES_EXTENSION = '.md'
    FLATPAGES_HTML_RENDERER = prerender_jinja
    FLATPAGES_MARKDOWN_EXTENSIONS = ['codehilite', 'tables']
    ARTICLES_PER_PAGE = 3
    PYGMENTS_STYLE = 'solarizeddark'


# Application setup
# =================

application = app = Flask(__name__)
app.config.from_object(DefaultConfig)
pages.init_app(app)


# Template filters & globals
# ==========================

@app.template_filter('date')
def date_filter(d, format_string):
    if d is None:
        d = datetime.datetime.utcnow()
    return d.strftime(format_string)


@app.template_global()
def url_for_other_page(page):
    args = request.view_args.copy()
    args['page'] = page
    return url_for(request.endpoint, **args)


@app.template_global()
def image(src, alt, title=''):
    url = url_for('static', filename='images/' + src)
    return render_template('figure.xhtml', src=src, alt=alt, title=title)


# View functions
# ==============

@app.route('/favicon.ico')
def favicon():
    return redirect(url_for('static', filename='images/favicon.ico'))


@app.route('/pygments.css')
def pygments_css():
    style = app.config['PYGMENTS_STYLE']
    return pygments_style_defs(style), 200, {'Content-Type': 'text/css'}


@app.route('/')
@app.route('/page/<int:page>/')
def index(page=1):
    articles = blog_articles()
    articles, pagination = paginate(articles, page,
                                    app.config['ARTICLES_PER_PAGE'])
    return render_template('index.xhtml', articles=articles,
                           pagination=pagination)


@app.route('/<path:path>/')
def page(path):
    page = pages.get_or_404(path)
    return render_page(page)


@app.route('/tag/<tag>/')
def tag(tag):
    articles = (a for a in blog_articles() if tag in a.meta.get('tags', []))
    return render_template('tag.xhtml', tag=tag, articles=articles)


@app.route('/tags/')
def tags():
    tags = Counter()
    for article in blog_articles():
        tags.update(article.meta.get('tags', []))
    return render_template('tags.xhtml', tags=tags)


@app.route('/archives/')
def archives():
    articles = list(blog_articles())
    return render_template('archives.xhtml', articles=articles)


# Error handling
# ==============

@app.errorhandler(404)
def not_found(error):
    page = pages.get('error-404')
    return render_page(page), 404


# Auxiliary functions
# ===================

def render_page(page):
    template = page.meta.get('template', 'page.xhtml')
    return render_template(template, page=page)


def blog_articles():
    # Blog articles are pages with a publication date
    articles = (page for page in pages
                if 'published' in page.meta and not page.meta.get('draft'))
    return reversed(sorted(articles, key=lambda a: a.meta['published']))


def paginate(items, page, per_page):
    items = list(items)
    count = len(items)
    lower_index = (page - 1) * per_page
    upper_index = page * per_page
    items = items[lower_index:upper_index]
    pagination = Pagination(page, per_page, count)
    if not items and page != 1:
        abort(404)
    return items, pagination


# Pagination
# ==========

class Pagination(object):
    '''Simple pagination class – see http://flask.pocoo.org/snippets/44/'''

    def __init__(self, page, per_page, total_count):
        self.page = page
        self.per_page = per_page
        self.total_count = total_count

    @property
    def pages(self):
        return int(math.ceil(self.total_count / float(self.per_page)))

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page < self.pages

    def iter_pages(self, left_edge=2, left_current=2,
                   right_current=5, right_edge=2):
        last = 0
        for num in xrange(1, self.pages + 1):
            if num <= left_edge or \
               (num > self.page - left_current - 1 and \
                num < self.page + right_current) or \
               num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num


# Development Server
# ==================

if __name__ == '__main__':
    try:
        port = int(sys.argv[1])
    except (IndexError, ValueError):
        port = 5000
    app.config.update({'DEBUG': True,
                       'FLATPAGES_AUTO_RELOAD': True})
    app.run(port=port)
