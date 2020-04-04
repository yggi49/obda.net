#!/usr/bin/env python
# -*- coding: utf-8 -*-

from fabric.api import env, local, put, cd, sudo, run


env.use_ssh_config = True
env.hosts = ["len"]


def deploy():
    archive = "/tmp/obda.net.tar.gz"
    pip = "/srv/obda/blog/venv/bin/pip"
    local("git archive -o {} HEAD".format(archive))
    put(archive, archive)
    with cd("/srv/obda/blog"):
        sudo("tar xzf {}".format(archive))
        sudo("{} install -r requirements.txt".format(pip))
        sudo("rm requirements.txt")
        sudo("chown -R obda:obda .")
    sudo("touch /etc/uwsgi.d/obda.ini")
    run("rm {}".format(archive))
    local("rm {}".format(archive))
