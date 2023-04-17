#!/usr/bin/env python
"""The obda.net blog."""

import codecs
import datetime
import math
import os
import sys
import uuid
from collections import Counter
from collections.abc import Iterable, Iterator
from typing import Any

import markdown
import sentry_sdk
import yaml
from flask import (
    Flask,
    abort,
    g,
    redirect,
    render_template,
    render_template_string,
    request,
    session,
    url_for,
)
from flask_flatpages import (
    FlatPages,
    Page,
    pygmented_markdown,
    pygments_style_defs,
)
from flask_gravatar import Gravatar
from markupsafe import Markup
from sentry_sdk.integrations.flask import FlaskIntegration
from werkzeug import Response

# Configuration
# =============


class EscapeHTML(markdown.extensions.Extension):
    """Markdown extension to escape HTML instead of rendering."""

    def extendMarkdown(self, md: markdown.Markdown) -> None:  # noqa: N802
        """Remove HTML preprocessors from the Markdown renderer."""
        md.preprocessors.deregister("html_block")
        md.inlinePatterns.deregister("html")


class DefaultConfig:
    """The Flask configuration object."""

    @staticmethod
    def prerender_jinja(text: str) -> str:
        """Render a text through Jinja first, and then through Markdown."""
        prerendered_body = render_template_string(Markup(text))
        return pygmented_markdown(prerendered_body, pages)

    @classmethod
    def prerender_escaped(cls, page: Page) -> str:
        """Render a text through Markdown, but without rendering HTML."""
        extensions = [*cls.FLATPAGES_MARKDOWN_EXTENSIONS, cls.MARKDOWN_ESCAPE]
        return markdown.markdown(page.body, extensions=extensions)

    DEBUG = False
    SECRET_KEY = "changeme"  # noqa: S105
    FLATPAGES_AUTO_RELOAD = False
    FLATPAGES_EXTENSION = ".md"
    FLATPAGES_HTML_RENDERER = prerender_jinja
    FLATPAGES_LEGACY_META_PARSER = True
    FLATPAGES_MARKDOWN_EXTENSIONS = ["codehilite", "tables", "footnotes"]
    FLATPAGES_EXTENSION_CONFIGS = {"codehilite": {"guess_lang": False}}
    MARKDOWN_ESCAPE = EscapeHTML()
    PYGMENTS_STYLE = "solarized-dark"
    ARTICLES_PER_PAGE = 3
    GRAVATAR_SIZE = 48
    GRAVATAR_DEFAULT = "identicon"
    VERSION = "development"


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

if sentry_dsn := os.environ.get("SENTRY_DSN"):
    sentry_sdk.init(
        dsn=sentry_dsn,
        release="obda-net@{}".format(app.config["VERSION"]),
        environment="production",
        integrations=[FlaskIntegration()],
    )


# Template filters & globals
# ==========================


@app.template_filter("markdown")
def markdown_filter(s: str) -> str:
    return Markup(markdown.markdown(s))


@app.template_filter("date")
def date_filter(d: datetime.datetime, format_string: str) -> str:
    """Format a date according to a given format string."""
    if d is None:
        d = datetime.datetime.now(datetime.timezone.utc)
    return d.strftime(format_string)


@app.template_filter()
def pluralize(number: int, singular: str = "", plural: str = "s") -> str:
    if number == 1:
        return singular
    return plural


@app.template_global()
def url_for_other_page(page: Page) -> str:
    args = request.view_args.copy()
    args["page"] = page
    return url_for(request.endpoint, **args)


@app.template_global()
def image(src: str, alt: str, title: str = "", class_name: str = "") -> str:
    return Markup(
        render_template(
            "figure.xhtml",
            src=src,
            alt=alt,
            title=title,
            class_name=class_name,
        ),
    )


@app.template_global()
def comments_enabled(page: Page) -> bool:
    """Return whether comments are enabled for a given page."""
    return (
        "published" in page.meta
        and not page.meta.get("draft", False)
        and page.meta.get("comments", True)
    )


@app.template_global()
def comment_count(page: Page) -> int:
    """Return the number of comments for a page."""
    return len(comment_directory_list(page))


@app.template_global()
def csrf_token(key: str) -> str:
    """Return a CSRF token."""
    if "csrf_tokens" not in session:
        session["csrf_tokens"] = {}
    token = str(uuid.uuid4())
    session["csrf_tokens"][key] = {
        "token": token,
        "timestamp": datetime.datetime.now(datetime.timezone.utc),
    }
    return token


# View functions
# ==============


@app.route("/favicon.ico")
def favicon() -> Response:
    """Return a redirect to the correct favicon."""
    return redirect(url_for("static", filename="images/favicon.ico"))


@app.route("/pygments.css")
def pygments_css() -> tuple[str, int, dict[str, str]]:
    """Return the Pygments style file as CSS."""
    style = app.config["PYGMENTS_STYLE"]
    return pygments_style_defs(style), 200, {"Content-Type": "text/css"}


@app.route("/")
@app.route("/page/<int:page>/")
def index(page: int = 1) -> str:
    """Render the blog index at a given page."""
    articles = blog_articles()
    articles, pagination = paginate(
        articles,
        page,
        app.config["ARTICLES_PER_PAGE"],
    )
    return render_template(
        "index.xhtml",
        articles=articles,
        pagination=pagination,
    )


@app.route("/<path:path>/", methods=["GET", "POST"])
def show_page(path: str) -> str | Response:
    """Render the page at the given path."""
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
def tag(tag_name: str) -> str:
    """Render a page with a list of all articles for a given tag."""
    articles = (
        a for a in blog_articles() if tag_name in a.meta.get("tags", [])
    )
    return render_template("tag.xhtml", tag=tag_name, articles=articles)


@app.route("/tags/")
def tags() -> str:
    """Render a page with a list of all defined tags."""
    tag_names = Counter()
    for article in blog_articles():
        tag_names.update(article.meta.get("tags", []))
    return render_template("tags.xhtml", tags=tag_names)


@app.route("/archives/")
def archives() -> str:
    """Render an archive page with links to all articles."""
    articles = list(blog_articles())
    return render_template("archives.xhtml", articles=articles)


# Error handling
# ==============


def errorpage(code: int) -> tuple[str, int]:
    """Render an error page for given HTTP code."""
    page = pages.get(f"error-{code}")
    return render_page(page), code


@app.errorhandler(403)
def forbidden(_error: Exception) -> tuple[str, int]:
    """Render an error page for HTTP 403 “Forbidden”."""
    return errorpage(403)


@app.errorhandler(404)
def not_found(_error: Exception) -> tuple[str, int]:
    """Render an error page for HTTP 404 “Forbidden”."""
    return errorpage(404)


# Auxiliary functions
# ===================


def render_page(page: Page, **kwargs: Any) -> str:  # noqa: ANN401
    """Render a specific page."""
    template = page.meta.get("template", "page.xhtml")
    return render_template(
        template,
        page=page,
        comments=get_comments(page),
        **kwargs,
    )


def comment_directory_list(page: Page) -> list[dict]:
    """Return a list of all comment files for a specific page."""
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
            for filename in sorted(files, reverse=True)
        ]
    g.comment_directory_list[page] = directory_list
    return directory_list


def get_comments(page: Page) -> list[Page]:
    """Return all comments for an article as a list of :class:`Page`s."""
    comments = []
    for comment in comment_directory_list(page):
        # noinspection PyProtectedMember
        comment_page = pages._load_file(  # noqa: SLF001
            comment["path"],
            comment["file"],
            comment["path"],  # TODO: check correctness
        )
        comment_page.html_renderer = DefaultConfig.prerender_escaped
        comments.append(comment_page)
    return comments


def validate_csrf(page: Page) -> bool:
    """Validate the CSRF token for a given page on a POST request."""
    if request.method != "POST":
        abort(403)
    path = page.path
    if "csrf_tokens" not in session or path not in session["csrf_tokens"]:
        abort(403)
    csrf = session["csrf_tokens"].pop(path)
    if not csrf or csrf["token"] != request.form.get("csrf_token"):
        abort(403)
    now = datetime.datetime.now(datetime.timezone.utc)
    csrf_age = now - csrf["timestamp"]
    if csrf_age.total_seconds() >= 15 * 60:
        return False
    return True


def post_comment(page: Page, data: dict) -> Response:
    """Add a new comment to a given article."""
    # the `verification` field serves as the honeypot; it should be empty
    if data["verification"]:
        return redirect(url_for("show_page", path=page.path))
    # we *think* that the user is not a bot
    comment_directory = os.path.join(pages.root, page.path)
    if not os.path.isdir(comment_directory):
        os.mkdir(comment_directory)
    now = datetime.datetime.now(datetime.timezone.utc)
    filename = "comment-{}".format(now.strftime("%Y-%m-%d-%H.%M.%S.%f"))
    full_path = os.path.join(comment_directory, filename)
    meta = {
        "author": data["name"],
        "email": data["email"],
        "website": data["website"],
        "published": now,
    }
    meta_yaml = yaml.safe_dump(
        meta,
        default_flow_style=False,
        allow_unicode=True,
        encoding="utf-8",
    )
    body = data["comment"].replace("\r\n", "\n")
    content = meta_yaml.decode("utf-8") + "\n" + body
    with codecs.open(full_path, "w", encoding="utf-8") as fh:
        fh.write(content)
    comment_id = "comment-{}".format(now.strftime("%Y%m%d%H%M%S%f"))
    return redirect(url_for("show_page", path=page.path, _anchor=comment_id))


def blog_articles() -> Iterable[Page]:
    # Blog articles are pages with a publication date
    articles = (
        page
        for page in pages
        if "published" in page.meta and not page.meta.get("draft")
    )
    return sorted(articles, key=lambda a: a.meta["published"], reverse=True)


def paginate(
    items: Iterable,
    page: int,
    per_page: int,
) -> tuple[list, "Pagination"]:
    """Paginte an iterable."""
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


class Pagination:
    """Simple pagination class - see http://flask.pocoo.org/snippets/44/."""

    def __init__(self, page: int, per_page: int, total_count: int) -> None:
        """Create a new :class:`Pagination` instance."""
        self.page = page
        self.per_page = per_page
        self.total_count = total_count

    @property
    def pages(self) -> int:
        """Return the total number of pages."""
        return int(math.ceil(self.total_count / float(self.per_page)))

    @property
    def has_prev(self) -> bool:
        """Return whether there is a “previous” page."""
        return self.page > 1

    @property
    def has_next(self) -> bool:
        """Return whether there is a “next” page."""
        return self.page < self.pages

    def iter_pages(
        self,
        left_edge: int = 2,
        left_current: int = 2,
        right_current: int = 5,
        right_edge: int = 2,
    ) -> Iterator[int | None]:
        """Iterate over pages, to be used for creating a navigation bar."""
        last = 0
        for num in range(1, self.pages + 1):
            if any(
                (
                    num <= left_edge,
                    self.page - left_current - 1
                    < num
                    < self.page + right_current,
                    num > self.pages - right_edge,
                ),
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
