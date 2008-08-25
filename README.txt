This file is for you to describe the pysvnmanager application. Typically
you would include information such as the information below:

Installation and Setup
======================

Install ``pysvnmanager`` using easy_install::

    easy_install pySvnManager

Make a config file as follows::

    paster make-config pySvnManager config.ini

Tweak the config file as appropriate and then setup the application::

    paster setup-app config.ini

Then you are ready to go.

Installation from Source code
=============================

Check source code from sourceforge.net::

    svn co https://sourceforge.net/projects/pysvnmanager/trunk pysvnmanager

Make a config file as follows::

    cd pysvnmanager/config
    make

Compile l18n messages::
    
    cd pysvnmanager
    python setup.py compile_catalog

Start web service::

    paster serve --reload develogment.ini


