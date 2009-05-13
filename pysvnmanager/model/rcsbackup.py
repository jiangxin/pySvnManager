#!/usr/bin/env python
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

from __future__ import division

import os
import sys
import re
import math

import logging
log = logging.getLogger(__name__)

sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from pysvnmanager.lib.text import to_unicode, to_utf8

#reload(sys) # in Python2.5, method sys.setdefaultencoding 
            #will be delete after initialize. we need reload it.
#sys.setdefaultencoding('utf-8')

CMD_CI="RCSINIT= ci"
CMD_CO="RCSINIT= co"
CMD_RCS="RCSINIT= rcs"
CMD_RLOG="RCSINIT= rlog"
CMD_RCSDIFF="RCSINIT= rcsdiff"

def is_rcs_exist(wcfile):
    wcpath = os.path.dirname(os.path.abspath(wcfile))
    if os.path.isdir(wcpath+'/RCS'):
        rcsfile = wcpath+'/RCS/'+os.path.basename(wcfile)+',v'
    else:
        rcsfile = wcfile+',v'
    return os.path.exists(rcsfile)

def backup(wcfile, comment='', user=''):
    if not wcfile:
        raise Exception, "working copy file is not given."
    if not user:
        user = "pySvnManager"
    if isinstance(comment, (list, tuple)):
        comment = '\n'.join(comment)
    if not comment:
        comment = "no message."
    
    wcfile = to_utf8(wcfile)
    comment = to_utf8(comment)
    user = to_utf8(user, escape=True)
    
    cmd = []
    if not is_rcs_exist(wcfile):
        # -l : lock mode, make wcfile writable
        cmd.append('%(cmd)s -i -q -l -t-"%(msg)s" -w"%(user)s" "%(file)s" 2>&1' % \
                {'cmd':CMD_CI, "file":wcfile, "msg":comment, "user":user})
        # -U : set locking to no-strict.
        cmd.append('%(cmd)s -U -u -M -q "%(file)s"' % {'cmd':CMD_RCS, "file":wcfile})
    else:
        # Warning: w/o -l or -u option, wcfile will be removed after checkin.
        # -l makes wcfile writable;
        # -u : wcfile is not writable unless rcsfile is set to no-strict locking.
        cmd.append('%(cmd)s -q -u -m"%(msg)s" -w"%(user)s" "%(file)s" 2>&1' % \
                {'cmd':CMD_CI, "file":wcfile, "msg":comment, "user":user})

    for i in cmd:
        log.debug("Command: "+i)
        try:
            buff = os.popen(i).read().strip()
        except Exception, e:
            raise
        else:
            if buff:
                os.system('%(cmd)s -U -u -M -q "%(file)s"' % {'cmd':CMD_RCS, "file":wcfile})
                raise Exception, "Error Message: %s\n" % buff

def restore(wcfile, revision=""):
    if not wcfile or not is_rcs_exist(wcfile):
        return
    opts = ""
    if revision:
        # -uRev : checkout without lock revision.
        # unlock wcfile is readonly, unless no-strict mode is set.
        opts = "-u%s" % revision

    cmd = '%(cmd)s %(opts)s -q -f "%(file)s" 2>&1' % {'cmd':CMD_CO, "opts":opts, "file":wcfile }
    buff = os.popen(cmd).read().strip()
    if buff:
        raise Exception, "Command: %s\nError Message: %s\n" % (to_unicode(cmd), to_unicode(buff))


def cat(wcfile, revision=""):
    if not wcfile or not is_rcs_exist(wcfile):
        return ""
    opts = "-p"
    if revision:
        # -pRev : cat rather then checkout
        opts = "-p%s" % revision

    cmd = '%(cmd)s %(opts)s -q "%(file)s"' % {'cmd':CMD_CO, "opts":opts, "file":wcfile }
    buff = os.popen(cmd).read().strip()
    return to_unicode(buff)

def differ(filename, rev1="", rev2=""):
    filename=to_utf8(filename)
    opts=""
    if rev1 and rev2:
        opts="-r%s -r%s" % (rev1, rev2)
    elif rev1 or rev2:
        opts="-r%s%s" % (rev1, rev2)
        
    cmd = '%(cmd)s %(opts)s -u -q "%(file)s"' % {'cmd':CMD_RCSDIFF, 'opts':opts, 'file':filename}
    log.debug('Command: '+cmd)
    buff = os.popen(cmd).read()
    return to_unicode(buff)

class RcsLog(object):
    
    def __init__(self, filename):
        assert filename and isinstance(filename, basestring)
        self.__file = filename
        self.__log_per_page = 10
        self.p = {}
        self.p['rcs'] = re.compile(r'^RCS file:\s*(.*)$', re.M)
        self.p['head'] = re.compile(r'^head:\s*(.*)$', re.M)
        self.p['total'] = re.compile(r'^total revisions:\s*(.*)$', re.M)
        self.p['revision'] = re.compile(r'^revision\s+([^\s]*)', re.M)
        self.p['date'] = re.compile(r'^date:\s+(.*);\s+author:', re.M)
        self.p['author'] = re.compile(r'^date:.*;\s+author:\s*(.*?);', re.M)
        self.reload()
    
    def __get_page_count(self):
        if self.__total == 0:
            count = 0
        elif self.__total <= self.__log_per_page:
            count = 1
        else:
            # show last record on every page.
            #count = int( math.ceil( (self.__total -1 ) / self.__log_per_page ) )
            count = int( math.ceil( (self.__total -2 ) / (self.__log_per_page - 1) ) )

        return count
    
    total_page = property(__get_page_count)

    def __get_log_count(self):
        return self.__total
    
    total = property(__get_log_count)
    
    def __get_rcsfile(self):
        return self.__rcsfile
    
    rcsfile = property(__get_rcsfile)
        
    def __get_head(self):
        return self.__head
    
    head = property(__get_head)
        
    def __get_log_per_page(self):
        return self.__log_per_page
    
    def __set_log_per_page(self, count):
        count = int(count)
        if count < 2:
            count = 2
        self.__log_per_page = count

    log_per_page = property(__get_log_per_page, __set_log_per_page)
    
    def reload(self):
        cmd = '%(cmd)s -h -N "%(file)s"' % {'cmd':CMD_RLOG, 'file':self.__file}
        buff = os.popen(cmd).read().strip()
        # RCS file: 1,v
        m = self.p['rcs'].search(buff)
        if m:
            self.__rcsfile = m.group(1)
        else:
            self.__rcsfile = ""

        # head: 1.XX
        m = self.p['head'].search(buff)
        if m:
            self.__head = m.group(1)
        else:
            self.__head = ""
            
        # total revisions: XX
        m = self.p['total'].search(buff)
        if m:
            self.__total = int(m.group(1))
        else:
            self.__total = 0
    
    def get_page_logs(self, pagenum):
        total_page = self.total_page
        
        if total_page ==0:
            return []

        if pagenum<=0:
            pagenum=1
        elif pagenum>total_page:
            pagenum=total_page
        
        heads = self.__head.rsplit('.',1)
        rev0=int(heads[1])
        
        rev2 = rev0 - ((pagenum-1) * (self.__log_per_page-1)) -1
        if rev2<1: rev2=1
        rev1 = rev2 - self.__log_per_page + 1
        if rev1<1:
            rev1=1

        rev0 = self.__head
        rev1 = "%s.%d" % (heads[0], rev1)
        rev2 = "%s.%d" % (heads[0], rev2)

        self.get_logs(rev1, rev2, rev0)
        return self.revs
    
    def get_logs(self, rev1="", rev2="", rev3=""):
        self.revs=[]
        opts=""
        if not rev1:
            if not rev2:
                opts=""
            else:
                opts="-r:%s" % rev2
        else:
            if not rev2:
                opts="-r%s:" % rev1
            else:
                opts="-r%s:%s" % (rev1, rev2)

        if rev3:
            opts="%s,%s" % (opts, rev3)

        cmd = '%(cmd)s %(opts)s -N "%(file)s"' % {'cmd':CMD_RLOG, 'opts':opts, 'file':self.__file}
        log.debug('Command: '+cmd)
        buff = os.popen(cmd).read().strip().rstrip('=').rstrip()
        
        while True:
            pos = buff.rfind('\n'+'-'*28+'\n')
            if pos==-1:
                break
            match = buff[pos+30:]
            buff=buff[:pos]

            lines=match.split('\n')
            if len(lines)<3:
                log.error("wrong rcs format: %s" % match)
                continue

            # revision 1.XX    locked by: XXX;
            m = self.p['revision'].search(lines[0])
            commit_revision = ""
            if m:
                commit_revision = m.group(1)
            else:
                log.error("not find revision in line: %s" % lines[1])
                continue
                        
            # date: YYYY/MM/DD hh:mm:ss;  author: XX;  ...
            m = self.p['date'].search(lines[1])
            commit_time = ""
            if m:
                commit_time = to_unicode(m.group(1))
            else:
                log.error("not find date in line: %s" % lines[1])
                continue

            # date: YYYY/MM/DD hh:mm:ss;  author: XX;  ...
            m = self.p['author'].search(lines[1])
            commit_author = ""
            if m:
                commit_author = to_unicode(eval("'%s'" % m.group(1)))
            else:
                log.error("not find author in line: %s" % lines[1])
                continue
            
            # logs...
            commit_log = to_unicode('\n'.join(lines[2:]))
            
            self.revs.append({'revision':commit_revision,
                              'date':commit_time,
                              'author':commit_author,
                              'log':commit_log})
        
        return self.revs
    
    def cat(self, revision=""):
        return cat(self.__file, revision)
    
    def differ(self, rev1="", rev2=""):
        return differ(self.__file, rev1, rev2)
    
    def restore(self, revision):
        return restore(self.__file, revision)

    def backup(self, comment='', user=''):
        return backup(self.__file, comment, user)
