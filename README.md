rasa
====

A [Django](https://www.djangoproject.com/) project template that includes a [Fabric](http://www.fabfile.org/) file that can perform deployment and updates to a [Ubuntu]() 14.04 server. 

### Install

1. Install Django, either globally or to a virtual environment.

2. Run the `startproject` command using the `rasa` project template.

        django-admin.py startproject --template=rasa/project_template/ --extension=py,ini,conf,nginx <project_name>

3. Initialize a [Git](http://git-scm.com/) repository in the included scaffolding.

3. Build your site!

4. Deploy by running the included `fabfile` with the URL of your Git repository. Need one? Try [GitHub](https://github.com/)! Example:

        fab -H <user>@<server> deploy:"https://github.com/<user>/<repository>.git"

### Software Stack

The deployment script will install the following software:

* [PostgreSQL](http://www.postgresql.org/) - a relational database
* [nginx](http://nginx.org/) - a server, which will serve static files and perform reverse proxy services in this setup
* [uWSGI](http://projects.unbit.it/uwsgi/) - a server, which will serve the Django application's responses

It deploys the python application in a [virtual environment](http://virtualenv.readthedocs.org/en/latest/virtualenv.html) and uses non-root users for its database and server commands.

The site will be deployed to the `/srv` directory.

### Updates

Updates can also be performed with the included `fabfile`:

    fab -H <user>@<server> update

-aodin, 2014
