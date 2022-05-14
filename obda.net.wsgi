#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import collections
import datetime
import math
import os
import sys
import uuid

import markdown
import yaml
from flask import (
    abort,
    Flask,
    g,
    redirect,
    render_template,
    render_template_string,
    request,
    session,
    url_for,
)
from flask_flatpages import FlatPages, pygmented_markdown, pygments_style_defs
from flask_gravatar import Gravatar
from markupsafe import Markup


# Configuration
# =============


class EscapeHTML(markdown.extensions.Extension):
    def extendMarkdown(self, md, md_globals):
        del md.preprocessors["html_block"]
        del md.inlinePatterns["html"]


class DefaultConfig(object):
    @staticmethod
    def prerender_jinja(text):
        prerendered_body = render_template_string(Markup(text))
        return pygmented_markdown(prerendered_body, pages)

    @classmethod
    def prerender_escaped(cls, page):
        extensions = cls.FLATPAGES_MARKDOWN_EXTENSIONS + [cls.MARKDOWN_ESCAPE]
        return markdown.markdown(page.body, extensions=extensions)

    DEBUG = False
    SECRET_KEY = "changeme"
    FLATPAGES_AUTO_RELOAD = False
    FLATPAGES_EXTENSION = ".md"
    FLATPAGES_HTML_RENDERER = prerender_jinja
    FLATPAGES_MARKDOWN_EXTENSIONS = ["codehilite", "tables", "footnotes"]
    FLATPAGES_EXTENSION_CONFIGS = {"codehilite": {"guess_lang": False}}
    MARKDOWN_ESCAPE = EscapeHTML()
    PYGMENTS_STYLE = "solarized-dark"
    ARTICLES_PER_PAGE = 3
    GRAVATAR_SIZE = 48
    GRAVATAR_DEFAULT = "identicon"


# Application setup
# =================

application = app = Flask(__name__)
app.config.from_object(DefaultConfig)
app.config.from_envvar("OBDA_SETTINGS", silent=True)
gravatar = Gravatar(
    app,
    size=app.config["GRAVATAR_SIZE"],
    default=app.config["GRAVATAR_DEFAULT"],
)
pages = FlatPages()
pages.init_app(app)


# Template filters & globals
# ==========================


@app.template_filter("markdown")
def markdown_filter(s):
    return Markup(markdown.markdown(s))


@app.template_filter("date")
def date_filter(d, format_string):
    if d is None:
        d = datetime.datetime.utcnow()
    return d.strftime(format_string)


@app.template_filter()
def pluralize(number, singular="", plural="s"):
    if number == 1:
        return singular
    else:
        return plural


@app.template_global()
def url_for_other_page(page):
    args = request.view_args.copy()
    args["page"] = page
    return url_for(request.endpoint, **args)


@app.template_global()
def image(src, alt, title="", class_name=""):
    return Markup(
        render_template(
            "figure.xhtml",
            src=src,
            alt=alt,
            title=title,
            class_name=class_name,
        )
    )


@app.template_global()
def comments_enabled(page):
    return (
        "published" in page.meta
        and not page.meta.get("draft", False)
        and page.meta.get("comments", True)
    )


@app.template_global()
def comment_count(page):
    return len(comment_directory_list(page))


@app.template_global()
def csrf_token(key):
    if "csrf_tokens" not in session:
        session["csrf_tokens"] = {}
    token = str(uuid.uuid4())
    session["csrf_tokens"][key] = {
        "token": token,
        "timestamp": datetime.datetime.utcnow(),
    }
    return token


# View functions
# ==============


@app.route("/favicon.ico")
def favicon():
    return redirect(url_for("static", filename="images/favicon.ico"))


@app.route("/pygments.css")
def pygments_css():
    style = app.config["PYGMENTS_STYLE"]
    return pygments_style_defs(style), 200, {"Content-Type": "text/css"}


@app.route("/")
@app.route("/page/<int:page>/")
def index(page=1):
    articles = blog_articles()
    articles, pagination = paginate(
        articles, page, app.config["ARTICLES_PER_PAGE"]
    )
    return render_template(
        "index.xhtml", articles=articles, pagination=pagination
    )


@app.route("/<path:path>/", methods=["GET", "POST"])
def show_page(path):
    page = pages.get_or_404(path)
    data = {
        key: ""
        for key in (
            "name",
            "email",
            "verification",
            "website",
            "comment",
            "captcha",
        )
    }
    required_fields = ("name", "email", "comment")
    form_errors = []
    if request.method == "POST":
        if not comments_enabled(page):
            abort(403)
        data = {key: request.form[key].strip() for key in data}
        form_errors = [key for key in required_fields if not data[key]]
        if not validate_csrf(page):
            form_errors.append("csrf")
        if data["captcha"] != "eight":
            form_errors.append("captcha")
        if not form_errors:
            return post_comment(page, data)
    return render_page(page, form_data=data, form_errors=form_errors)


@app.route("/tag/<tag_name>/")
def tag(tag_name):
    articles = (
        a for a in blog_articles() if tag_name in a.meta.get("tags", [])
    )
    return render_template("tag.xhtml", tag=tag_name, articles=articles)


@app.route("/tags/")
def tags():
    tag_names = collections.Counter()
    for article in blog_articles():
        tag_names.update(article.meta.get("tags", []))
    return render_template("tags.xhtml", tags=tag_names)


@app.route("/archives/")
def archives():
    articles = list(blog_articles())
    return render_template("archives.xhtml", articles=articles)


# Error handling
# ==============


def errorpage(code):
    page = pages.get("error-{}".format(code))
    return render_page(page), code


@app.errorhandler(403)
def forbidden(error):
    return errorpage(403)


@app.errorhandler(404)
def not_found(error):
    return errorpage(404)


# Auxiliary functions
# ===================


def render_page(page, **kwargs):
    template = page.meta.get("template", "page.xhtml")
    return render_template(
        template, page=page, comments=get_comments(page), **kwargs
    )


def comment_directory_list(page):
    if "comment_directory_list" not in g:
        g.comment_directory_list = {}
    if page in g.comment_directory_list:
        return g.comment_directory_list[page]
    comment_directory = os.path.join(pages.root, page.path)
    directory_list = []
    if os.path.isdir(comment_directory):
        directory_list = [
            {
                "path": "/".join((page.path, filename)),
                "file": os.path.join(root, filename),
            }
            for root, dirs, files in os.walk(comment_directory)
            for filename in reversed(sorted(files))
        ]
    g.comment_directory_list[page] = directory_list
    return directory_list


def get_comments(page):
    comments = []
    for comment in comment_directory_list(page):
        comment_page = pages._load_file(comment["path"], comment["file"])
        comment_page.html_renderer = DefaultConfig.prerender_escaped
        comments.append(comment_page)
    return comments


def validate_csrf(page):
    assert request.method == "POST", "CSRF validation on non-POST request"
    path = page.path
    if "csrf_tokens" not in session or path not in session["csrf_tokens"]:
        abort(403)
    csrf = session["csrf_tokens"].pop(path)
    if not csrf or csrf["token"] != request.form.get("csrf_token"):
        abort(403)
    csrf_age = datetime.datetime.utcnow() - csrf["timestamp"]
    if csrf_age.total_seconds() >= 15 * 60:
        return False
    return True


def post_comment(page, data):
    # the `verification` field serves as the honeypot – it should be empty
    if data["verification"]:
        return redirect(url_for("show_page", path=page.path))
    # we *think* that the user is not a bot
    comment_directory = os.path.join(pages.root, page.path)
    if not os.path.isdir(comment_directory):
        os.mkdir(comment_directory)
    now = datetime.datetime.utcnow()
    filename = "comment-{}".format(now.strftime("%Y-%m-%d-%H.%M.%S.%f"))
    full_path = os.path.join(comment_directory, filename)
    meta = {
        "author": data["name"],
        "email": data["email"],
        "website": data["website"],
        "published": now,
    }
    meta_yaml = yaml.safe_dump(
        meta, default_flow_style=False, allow_unicode=True, encoding="utf-8"
    )
    body = data["comment"].replace("\r\n", "\n")
    content = meta_yaml.decode("utf-8") + "\n" + body
    with codecs.open(full_path, "w", encoding="utf-8") as fh:
        fh.write(content)
    comment_id = "comment-{}".format(now.strftime("%Y%m%d%H%M%S%f"))
    return redirect(url_for("show_page", path=page.path, _anchor=comment_id))


def blog_articles():
    # Blog articles are pages with a publication date
    articles = (
        page
        for page in pages
        if "published" in page.meta and not page.meta.get("draft")
    )
    return reversed(sorted(articles, key=lambda a: a.meta["published"]))


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
    """Simple pagination class – see http://flask.pocoo.org/snippets/44/"""

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

    def iter_pages(
        self, left_edge=2, left_current=2, right_current=5, right_edge=2
    ):
        last = 0
        for num in range(1, self.pages + 1):
            if any(
                (
                    num <= left_edge,
                    self.page - left_current - 1
                    < num
                    < self.page + right_current,
                    num > self.pages - right_edge,
                )
            ):
                if last + 1 != num:
                    yield None
                yield num
                last = num


# Development Server
# ==================

if __name__ == "__main__":
    try:
        port = int(sys.argv[1])
    except (IndexError, ValueError):
        port = 5000
    app.config.update({"DEBUG": True, "FLATPAGES_AUTO_RELOAD": True})
    app.run(port=port)
