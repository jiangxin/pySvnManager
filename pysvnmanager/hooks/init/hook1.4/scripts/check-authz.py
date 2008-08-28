#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, locale
from svn import repos, fs, core
locale.setlocale(locale.LC_ALL, 'zh_CN.UTF8')

def test_authz(path):
  try:
    repos.svn_repos_authz_read(path, 1)
  except core.SubversionException, ( strerror, errorno ):
    if errorno == 0:
      errorno = 1
    return (errorno, strerror)
  except:
    return (1, sys.exc_info()[1])

  return (0, 0)

filename = sys.argv[1]
(errorno, strerror) = test_authz(filename)
if errorno:
  sys.stderr.write('Parse authz config file "%s" failed\n' % (filename))
  sys.stderr.write('Possible errors:\n')
  sys.stderr.write('  %s\n' % strerror)
  sys.exit(1)
else:
  sys.exit(0)
