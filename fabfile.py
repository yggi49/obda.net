"""obda.net deployment script."""

from fabric import Connection, task
from invoke import run as local


@task
def deploy(ctx: Connection, version: str) -> None:
    """Deploy the blog to the production system.

    Do not forget to supply ``--prompt-for-sudo-password`` when running
    it from the CLI, for example::

       fab -H <host> --prompt-for-sudo-password deploy

    .. note::
       This deploys whatever the Git HEAD currently points to.

    :param ctx: the connection to the remote host.
    :param version: the version number that shall be reported by the
                    installed application.
    """
    python_version = "3.11"
    app_user = "obda"
    base_dir = "/srv/obda/blog"
    # Create application directory (if necessary)
    create_dir(ctx, base_dir, app_user)
    # Create virtualenv (if necessary)
    venv_dir = create_virtualenv(ctx, base_dir, python_version)
    pip = f"{venv_dir}/bin/pip"
    # Create artifacts and upload them to the remote host
    archive = f"/tmp/obda.net-{version}.tar.gz"  # noqa: S108
    requirements = f"/tmp/obda.net-{version}.requirements.txt"  # noqa: S108
    local(f"git archive -o {archive} HEAD")
    local(f"poetry export --with server -o {requirements}")
    for path in (archive, requirements):
        ctx.put(path, path)
    # Unpack archive and install requirements
    ctx.sudo(f"tar -C /srv/obda/blog -xzf {archive}")
    ctx.sudo(f"{pip} install -r {requirements}")
    # Set correct version
    ctx.sudo(
        "perl -p -i -e "
        f"""'s/VERSION = "development"/VERSION = "{version}"/g' """
        "/srv/obda/blog/obda.py",
    )
    # Fix ownership
    ctx.sudo(f"chown -R {app_user}:{app_user} {base_dir}")
    # Restart application
    ctx.sudo("supervisorctl stop obda:obda-net")
    ctx.sudo("supervisorctl reread")
    ctx.sudo("supervisorctl start obda:obda-net")
    # Clean up
    for path in (archive, requirements):
        ctx.run(f"rm {path}")
        local(f"rm {path}")


def create_dir(ctx: Connection, path: str, owner: str) -> None:
    """Create a directory on the remote host.

    If the directory already exists, only the directory’s ownership will
    be updated (non-recursively).

    :param ctx: the connection to the remote host.
    :param path: the full path of the directory to create.
    :param owner: the username of the directory owner.
    """  # noqa: RUF002
    ctx.sudo(f"mkdir -p {path}")
    ctx.sudo(f"chown {owner}:{owner} {path}")


def create_virtualenv(ctx: Connection, path: str, python_version: str) -> str:
    """Create a Python virtualenv under the given path.

    The virtualenv directory will be named ``venv-py<version>``, e.g.
    ``venv-py3.10``, and a symlink with the generic name ``venv`` will
    be created as well.

    :param ctx: the connection to the remote host.
    :param path: the full path to the base directory where the ``venv``
                 virtualenv shall be created.
    :param python_version: the Python version to use for the virtualenv
                           in the form ``major.minor``, e.g. ``"3.10"``.
    :return: the full path to the created virtualenv.
    """
    venv_dir = f"{path}/venv-py{python_version}"
    python_executable_name = f"python{python_version}"
    python_binary = f"{venv_dir}/bin/{python_executable_name}"
    venv_check = ctx.sudo(f"file {python_binary}", hide="out")
    output = venv_check.stdout.strip()
    venv_is_missing = output.endswith("(No such file or directory)")
    if not venv_is_missing:
        return venv_dir
    ctx.sudo(f"rm -rf {venv_dir}")
    ctx.sudo(f"{python_executable_name} -m venv {venv_dir}")
    # Create Python version-agnostic symlinks for the virtualenv as well
    # as inside its ``lib`` directory, which can be used in the nginx
    # configuration for delivering static assets that are part of the
    # Python package.
    venv_lib_dir = f"{venv_dir}/lib/python{python_version}"
    venv_lib_dir_symlink = f"{venv_dir}/lib/python"
    ctx.sudo(f"ln -s -r -f -n {venv_lib_dir} {venv_lib_dir_symlink}")
    ctx.sudo(f"ln -s -r -f -n {venv_dir} {path}/venv")
    return venv_dir
