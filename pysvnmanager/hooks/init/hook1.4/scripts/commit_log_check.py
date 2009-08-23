#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Validate commit log:
--------------------
* Check the length of commit log;
* Check certain contents against Regular Expression;

Usage:
------
%(program)s [options...] repos txn

Options:
--------
  -s, --size:
      The minimal strlen of log message.

  -p, --permit:
      Pattern for log message should match against.
      Multiple patterns can be given if provide multiple -p,
      if one of the pattern is matched, validation passed.

  -P, --prohibit:
      Pattern that log message should *not* match against.
      Multiple patterns can be given if provide multiple -p,
      if one of the pattern is matched, validation failed.


by Jiang Xin<WorldHello.net.AT.gmail.com>
"""

__revision__ = '$Id: commit_log_check.py 1563 2006-07-04 05:37:20Z jiangxin $'

import sys, os, re
import getopt

if os.name == 'nt':
    SVNLOOK = 'C:/Apps/Subversion/bin/svnlook.exe'
else:
    SVNLOOK = '/opt/svn/bin/svnlook'

os.environ['LANG'] = os.environ['LC_ALL'] = 'zh_CN.UTF8'
program = sys.argv[0]

def usage(code=0, msg=''):
    if code:
        fd = sys.stderr
    else:
        fd = sys.stdout
    print >> fd, __doc__ % { 'program':program }
    if msg:
        print >> fd, msg
    return code

def main(argv=None):
    """main entry point"""

    if argv is None:
        argv = sys.argv[1:]

    opt_size = 4
    # r'(issue\s*[#]?[0-9]+)|(new.*:)|(bugfix:)',
    opt_permit_pattern = []
    opt_prohibit_pattern = []
    log_msg = ''

    try:
        opts, args = getopt.getopt( 
                argv, "hs:p:m:P:", 
                ["help", "size=", "permit=", "prohibit=", "message="])
    except getopt.error, msg:
        return usage(1, msg)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            return usage()
        elif opt in ("-s", "--size"):
            opt_size = int(arg)
        elif opt in ("-p", "--permit"):
            if arg and not isinstance(arg, unicode):
                arg = unicode(arg, 'utf-8')
            if arg:
                opt_permit_pattern.append(arg)
        elif opt in ("-P", "--prohibit"):
            if arg:
                if not isinstance(arg, unicode):
                    arg = unicode(arg, 'utf-8')
                opt_prohibit_pattern.append(arg)
        elif opt in ("-m", "--message"):
            if arg:
                if not isinstance(arg, unicode):
                    arg = unicode(arg, 'utf-8')
                log_msg = arg
        else:
            return usage(1)

    if len(args) != 2:
        return usage(1)

    repos = args[0]
    txn   = args[1]

    if not log_msg:
        log_cmd = '%s log -t "%s" "%s"' % (SVNLOOK, txn, repos)
        log_msg = os.popen(log_cmd, 'r').read().rstrip('\n')

    # Check the length of commit log
    check_strlen(log_msg, opt_size)
    
    # Check certain contents against Regular Expression
    check_pattern(log_msg, opt_permit_pattern, opt_prohibit_pattern)


def check_strlen(log_msg, size):
    """
    Check length of log_msg, not less then size
    """
    log_msg = log_msg.strip()
    log_length = len(log_msg)

    if log_length > 0:
        char  = log_msg[0]
        char2 = log_msg[-1]        
        idx = 1
        while idx < len(log_msg):
            if char == -1 and char2 == -1 and log_length <= 0:
                break

            if (char == log_msg[idx]) and (char != -1):
                log_length = log_length - 1
                char = log_msg[idx]
            else:
                char = -1

            if (char2 == log_msg[-idx]) and (char2 != -1):
                log_length = log_length - 1
                char2 = log_msg[-idx]
            else:
                char2 = -1

            idx = idx + 1
    
    if log_length < size:
        error_msg = u"提交说明至少应包含 %d 个字符, 或者太简单了。\n" % size
        sys.stderr.write (error_msg.encode('utf-8'))
        sys.exit(1)


def check_pattern(log_msg, permit=None, prohibit=None):
    """
    Check log_msg against patterns
    """

    if permit:
        matched = False
        for pat in permit:
            if not pat: # blank pattern
                matched = True
                break
            elif re.compile(pat, re.I).search(log_msg):
                matched = True
                break
        if not matched:
            error_msg = u"无法在提交说明中匹配表达式: \n%s。\n" % ',\n'.join(permit)
            sys.stderr.write (error_msg.encode('utf-8'))
            sys.exit(1)

    if prohibit:
        matched = False
        for pat in prohibit:
            if pat and re.compile(pat, re.I).search(log_msg):
                matched = True
                break
        if matched:
            error_msg = u"不允许在log中出现类似表达式: \n%s。\n" % pat
            sys.stderr.write (error_msg.encode('utf-8'))
            sys.exit(1)

if __name__ == '__main__':
    main()

# vim: ft=python ts=4 sw=4 et
