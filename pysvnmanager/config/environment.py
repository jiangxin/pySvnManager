"""Pylons environment configuration"""
# -*- coding: utf-8 -*-
import os

from pylons import config

import pysvnmanager.lib.app_globals as app_globals
import pysvnmanager.lib.helpers
from pysvnmanager.config.routing import make_map

def load_environment(global_conf, app_conf):
    """Configure the Pylons environment via the ``pylons.config``
    object
    """
    # Pylons paths
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    paths = dict(root=root,
                 controllers=os.path.join(root, 'controllers'),
                 static_files=os.path.join(root, 'public'),
                 templates=[os.path.join(root, 'templates')])

    # Initialize config with the basic options
    config.init_app(global_conf, app_conf, package='pysvnmanager',
                    template_engine='mako', paths=paths)

    config['routes.map'] = make_map()
    config['pylons.g'] = app_globals.Globals()
    config['pylons.h'] = pysvnmanager.lib.helpers

    # Customize templating options via this variable
    tmpl_options = config['buffet.template_options']
    
    # 设置缺省编码为 utf8
    tmpl_options['mako.input_encoding'] = 'UTF-8'
    tmpl_options['mako.output_encoding'] = 'UTF-8'
    #tmpl_options['mako.default_filters'] = ['decode.utf8']


    # CONFIGURATION OPTIONS HERE (note: all config options will override
    # any Pylons config options)
