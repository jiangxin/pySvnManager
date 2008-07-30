#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

import logging
log = logging.getLogger(__name__)

import sys
#reload(sys) # in Python2.5, method sys.setdefaultencoding 
            #will be delete after initialize. we need reload it.
#sys.setdefaultencoding('utf-8')

CMD_CI="RCSINIT= ci"
CMD_CO="RCSINIT= co"
CMD_RCS="RCSINIT= rcs"


def is_rcs_exist(wcfile):
    wcpath = os.path.dirname(os.path.abspath(wcfile))
    if os.path.isdir(wcpath+'/RCS'):
        rcsfile = wcpath+'/RCS/'+os.path.basename(wcfile)+',v'
    else:
        rcsfile = wcfile+',v'
    return os.path.exists(rcsfile)

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
        # -l : lock mode, make wcfile writable
        cmd.append('%(cmd)s -i -q -l -t-"%(msg)s" -w"%(user)s" %(file)s 2>&1' % \
                {'cmd':CMD_CI, "file":wcfile, "msg":comment, "user":user})
        # -U : set locking to no-strict.
        cmd.append('%(cmd)s -U -q %(file)s' % {'cmd':CMD_RCS, "file":wcfile})
    else:
        # Warning: w/o -l or -u option, wcfile will be removed after checkin.
        # -l makes wcfile writable;
        # -u : wcfile is not writable unless rcsfile is set to no-strict locking.
        cmd.append('%(cmd)s -q -l -m"%(msg)s" -w"%(user)s" %(file)s 2>&1' % \
                {'cmd':CMD_CI, "file":wcfile, "msg":comment, "user":user})

    for i in cmd:
        log.debug("Command: "+i)
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
        # -uRev : checkout without lock revision.
        # unlock wcfile is readonly, unless no-strict mode is set.
        opts = "-u%s" % revision

    cmd = "%(cmd)s %(opts)s -q -f %(file)s 2>&1" % {'cmd':CMD_CO, "opts":opts, "file":wcfile }
    buff = os.popen(cmd).read().strip()
    if buff:
        raise Exception, "Command: %s\nError Message: %s\n" % (cmd, buff)
    
