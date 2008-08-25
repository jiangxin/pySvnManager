#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

svn_hooks_init_dict = { '1.4': 'hook1.4',
                        '1.5': 'hook1.5',
                        'default': 'hook1.5',
                      }

svn_hooks_init_base = os.path.dirname(os.path.abspath(__file__))
