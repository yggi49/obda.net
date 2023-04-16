"""obda.net deployment script."""

from fabric import Connection, task
from invoke import run as local


@task
def deploy(ctx: Connection) -> None:
    """Deploy the blog to the production system.

    Do not forget to supply ``--prompt-for-sudo-password`` when running
    it from the CLI, for example::

       fab -H <host> --prompt-for-sudo-password deploy
    """
    archive = "/tmp/obda.net.tar.gz"  # noqa: S108
    requirements = "/tmp/obda.net.requirements.txt"  # noqa: S108
    local(f"git archive -o {archive} HEAD")
    local(f"poetry export -o {requirements}")
    for path in (archive, requirements):
        ctx.put(path, path)
    ctx.sudo(f"tar -C /srv/obda/blog -xzf {archive}")
    ctx.sudo(f"/srv/obda/blog/venv/bin/pip install -r {requirements}")
    ctx.sudo("chown -R obda:obda /srv/obda/blog")
    ctx.sudo("touch /etc/uwsgi.d/obda.ini")
    for path in (archive, requirements):
        ctx.run(f"rm {path}")
        local(f"rm {path}")
