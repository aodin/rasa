# -*- coding: utf-8 -*
import os

from fabric.api import local, settings, abort, run, cd, env
from fabric.contrib.console import confirm
from fabric.operations import sudo

# Use the local SSH config file
env.use_ssh_config = True


def shutdown_r():
    """
    Restart the server.
    """
    sudo('shutdown -r now')


def update_ubuntu():
    """
    Perform updates for ubuntu.
    """
    sudo('apt-get -q -y update')
    sudo('apt-get -q -y dist-upgrade')
    sudo('apt-get -q -y autoremove')


def setup_ubuntu():
    """
    Install the required Ubuntu dependencies from the package repository.
    These packages are for Ubuntu 14.04
    """
    sudo('apt-get -q -y install make gcc python-dev git mercurial nginx python-pip python-setuptools python-virtualenv')
    sudo('apt-get -q -y install postgresql-9.3 postgresql-server-dev-9.3 python-psycopg2')


def upgrade_pip():
    """
    Upgrade PIP by using PIP!
    """
    sudo('pip install -q -U pip')
    sudo('pip install -q -U virtualenv')


def clone(url, directory='/srv', user='www-data'):
    """
    Clone the given repo into the /srv directory by default.
    """
    with cd(directory):
        sudo('chown {user}:{user} .'.format(user=user))
        sudo('git clone {url}'.format(url=url), user=user)


def setup_env(project, directory='/srv/', user='www-data'):
    """
    Create the python virtual environment.
    """
    # Create the virtual environment
    envdir = os.path.join(directory, project, 'env')
    sudo('virtualenv {dir}'.format(dir=envdir), user=user)

    # Load dependencies from a file
    reqs = os.path.join(directory, project, 'requirements.txt')
    sudo('{dir}/bin/pip install -U -r {reqs}'.format(dir=envdir, reqs=reqs), user=user)


def server_ln(project):
    """
    Create the symbolic links for the server configurations.

    To the new init job without restarting, call:
    initctl reload-configuration

    View all services:
    service --status-all
    """
    server_src = '/srv/{project}/conf/{project}.conf'.format(project=project)
    server_dest = '/etc/init/{project}.conf'.format(project=project)

    nginx_src = '/srv/{project}/conf/{project}.nginx'.format(project=project)
    nginx_dest = '/etc/nginx/sites-enabled/{project}'.format(project=project)

    # Remove any existing links at the destinations
    with settings(warn_only=True):
        sudo('rm {dest}'.format(dest=server_dest))
        sudo('rm {dest}'.format(dest=nginx_dest))

        # Remove the default site from nginx
        sudo('rm /etc/nginx/sites-enabled/default')

    # Create the symbolic links
    sudo('ln -s {src} {dest}'.format(src=server_src, dest=server_dest))
    sudo('ln -s {src} {dest}'.format(src=nginx_src, dest=nginx_dest))
    sudo('initctl reload-configuration')


def create_pg_db(db):
    """
    Create the given database.
    """
    # TODO test to see if database already exists
    sudo('createdb {db}'.format(db=db), user='postgres')


def alter_pg_user(password, user='postgres'):
    """
    Alter the user with the given password.
    """
    sudo("""psql -c "ALTER USER {user} with password '{password}';" """.format(user=user, password=password), user='postgres')


def setup_django(project, directory='/srv'):
    """
    Run django's syncdb and collectstatic in its virtualenv
    """
    src = os.path.join(directory, project)
    python = os.path.join(src, 'env', 'bin', 'python')
    manage = os.path.join(src, 'manage.py')

    # Do not accept input during syncdb, we will create a superuser ourselves
    sudo('{python} {manage} syncdb --verbosity=0 --noinput'.format(python=python, manage=manage))
    sudo('{python} {manage} collectstatic --verbosity=0 --noinput'.format(python=python, manage=manage))


def restart(project='{{ project_name }}'):
    """
    Restarts the servers.
    """
    sudo('service {project} restart'.format(project=project))
    sudo('nginx -t')
    sudo('service nginx restart')


def update(project='{{ project_name }}', syncdb=False, reset=False, remote='origin', branch='master', user='www-data', directory='/srv'):
    """
    Update the project by pulling from the git repository
    """
    src = os.path.join(directory, project)
    python = os.path.join(src, 'env', 'bin', 'python')
    manage = os.path.join(src, 'manage.py')

    with cd(src):
        if reset:
            sudo('git reset --hard HEAD', user=user)
        sudo('git pull {remote} {branch}'.format(remote=remote, branch=branch), user=user)

    # Only call syncdb when instructed
    if syncdb:
        sudo('{python} {manage} syncdb --verbosity=0 --noinput'.format(python=python, manage=manage), user=user)

    sudo('{python} {manage} collectstatic --verbosity=0 --noinput'.format(python=python, manage=manage), user=user)

    sudo('service {project} restart'.format(project=project))


def deploy(git_repo, skip_setup=False, project='{{ project_name }}'):
    """
    The master deploy script.
    Example:
    fab -H user@server deploy:https://github.com/user/repo.git
    """
    # Ubuntu setup
    if not skip_setup:
        update_ubuntu()
        setup_ubuntu()
        upgrade_pip()

    # Fun starts here
    clone(git_repo)
    setup_env(project)
    server_ln(project)
    create_pg_db(project)
    alter_pg_user('badpassword')
    setup_django(project)

    # Restart
    restart(project)
