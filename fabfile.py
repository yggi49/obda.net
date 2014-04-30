#!/usr/bin/env python
# -*- coding: utf-8 -*-

from fabric.api import *


env.use_ssh_config = True
env.hosts = ['monty']


def deploy():
    archive = '/tmp/obda.net.tar.gz'
    pip = '/usr/local/pythonenv/prod-obda-website/bin/pip'
    local('git archive -o {} HEAD'.format(archive))
    put(archive, archive)
    with cd('/srv/obda.net/www'):
        sudo('tar xzf {}'.format(archive))
        sudo('{} install -r requirements.txt'.format(pip))
        sudo('rm requirements.txt')
    sudo('apache2ctl graceful')
    run('rm {}'.format(archive))
    local('rm {}'.format(archive))
