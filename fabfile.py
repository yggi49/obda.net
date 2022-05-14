from fabric import task, Connection
from invoke import run as local


@task
def deploy(ctx):
    """Deploy the blog to the production system.

    Do not forget to supply ``--prompt-for-sudo-password`` when running
    it from the CLI, for example::

       fab -H <host> --prompt-for-sudo-password deploy
    """
    archive = "/tmp/obda.net.tar.gz"
    requirements = "/tmp/obda.net.requirements.txt"
    local("git archive -o {} HEAD".format(archive))
    local("poetry export -o {}".format(requirements))
    for path in (archive, requirements):
        ctx.put(path, path)
    ctx.sudo("tar -C /srv/obda/blog -xzf {}".format(archive))
    ctx.sudo("/srv/obda/blog/venv/bin/pip install -r {}".format(requirements))
    ctx.sudo("chown -R obda:obda /srv/obda/blog")
    ctx.sudo("touch /etc/uwsgi.d/obda.ini")
    for path in (archive, requirements):
        ctx.run("rm {}".format(path))
        local("rm {}".format(path))
