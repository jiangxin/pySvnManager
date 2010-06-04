# -*- coding: utf-8 -*-
#
# Copyright (C) 2008 OpenSourceXpress Ltd. (http://www.ossxp.com)
# Author: Jiang Xin
# Contact: http://www.ossxp.com
#          http://www.worldhello.net
#          http://moinmo.in/JiangXin
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

"""Setup the pySvnManager application"""
import logging

import pylons.test

from pysvnmanager.config.environment import load_environment

from paste.deploy import appconfig
from shutil import copyfile
import os
from pkg_resources import resource_filename

from pysvnmanager.config.environment import load_environment

log = logging.getLogger(__name__)

def setup_app(command, conf, vars):
    """Place any commands to setup pysvnmanager here"""
    # Don't reload the app if it was loaded under the testing environment
    if not pylons.test.pylonsapp:
        load_environment(conf.global_conf, conf.local_conf)
    else:
        # Hack pylons: config['here'] is used in many places, so setup here.
        from pylons import config
        wsgiapp = pylons.test.pylonsapp
        config['here'] = wsgiapp.config.get('here')

    here = conf['here']

    if not os.path.exists(here+'/config'):
        os.mkdir(here+'/config')
    if not os.path.exists(here+'/config/RCS'):
        os.mkdir(here+'/config/RCS')
    if not os.path.exists(here+'/svnroot'):
        os.mkdir(here+'/svnroot')
    filelist = ['svn.access', 'svn.passwd', 'localconfig.py']
    for f in filelist:
        src  = resource_filename('pysvnmanager', 'config/' + f+'.in')
        dest = here+'/config/' + f
        if os.path.exists(dest):
            log.warning("Warning: %s already exist, ignored." % f)
        else:
            copyfile(src, dest)
