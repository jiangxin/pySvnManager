This file is for you to describe the pySvnManager application. Typically
you would include information such as the information below:

Prerequisite
============

You need the following packages. Only part of them (docutils)
will be installed automatically during easy_install.

- pylons:
    A must have package.

- rcs:
    We use ci/co for backup/restore SVN authz files.

- python docutils:
    We docutils to transform reST text to html.

- python-ldap:
    If pySvnManager is auth agains ldap, you need it.

- easy_install:
    Optional. Useful tools to manage python egg packages.

Installation and Setup
======================

Install ``pysvnmanager`` using easy_install::

    easy_install pySvnManager

Make a config file as follows::

    paster make-config pySvnManager config.ini

Tweak the config file as appropriate and then setup the application::

    paster setup-app config.ini

Then you are ready to go.

    paster serve --reload config.ini

Installation from Source code
=============================

Check source code from sourceforge.net::

    svn co https://sourceforge.net/projects/pysvnmanager/trunk pysvnmanager

Make a config file as follows::

    cd config
    make

Compile l18n messages::
    
    python setup.py compile_catalog

Start web service::

    paster serve --reload develogment.ini


