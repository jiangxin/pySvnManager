#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

import logging
log = logging.getLogger(__name__)

import sys
#reload(sys) # in Python2.5, method sys.setdefaultencoding 
            #will be delete after initialize. we need reload it.
#sys.setdefaultencoding('utf-8')

def is_rcs_exist(wcfile):
    rcsfile = wcfile+',v'
    return os.access(rcsfile, os.F_OK)

def get_unicode(msg, escape=False):
    if isinstance(msg, basestring) and not isinstance(msg, unicode):
        msg = unicode(msg, 'utf-8')
    if escape and isinstance(msg, basestring):
        msg = msg.encode('raw_unicode_escape')
    return msg

def get_utf8(msg, escape=False):
    if isinstance(msg, unicode):
        msg = msg.encode('utf-8')
    if escape and isinstance(msg, basestring):
        msg = repr(msg)[1:-1]
    return msg

def backup(wcfile, comment='', user=''):
    if not wcfile:
        raise Exception, "working copy file is not given."
    if not user:
        user = "pySvnManager"
    if isinstance(comment, (list, tuple)):
        comment = '\n'.join(comment)
    if not comment:
        comment = "no message."
    
    wcfile = get_utf8(wcfile)
    comment = get_utf8(comment)
    user = get_utf8(user, escape=True)
    
    cmd = []
    if not is_rcs_exist(wcfile):
        cmd.append("""ci -i -q -t-"%(msg)s" -w"%(user)s" %(file)s 2>&1""" % \
                {"file":wcfile, "msg":comment, "user":user})
        cmd.append('rcs -U -q %s' % wcfile)
    else:
        cmd.append("""ci -q -m"%(msg)s" -w"%(user)s" %(file)s 2>&1""" % \
                {"file":wcfile, "msg":comment, "user":user})

    for i in cmd:
        log.debug("Command: "+i)
        continue
        try:
            buff = os.popen(i).read().strip()
        except Exception, e:
            raise
        else:
            if buff:
                raise Exception, "Error Message: %s\n" % buff

def restore(wcfile, revision=""):
    if not wcfile or not is_rcs_exist(wcfile):
        return
    opts = ""
    if revision:
        opts = "-u%s" % revision

    cmd = "co %(opts)s -q -f %(file)s 2>&1" % {"opts":opts, "file":wcfile }
    buff = os.popen(cmd).read().strip()
    if buff:
        if 'co: warning: -l overridden by -u' in buff:
            pass
        else:
            raise Exception, "Command: %s\nError Message: %s\n" % (cmd, buff)
    
