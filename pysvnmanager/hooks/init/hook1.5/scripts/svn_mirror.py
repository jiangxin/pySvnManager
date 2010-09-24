#!/usr/bin/python
# -*- coding: utf-8 -*-

'''Svnsync program

Usage: %(program)s [options]

Options:

    -h|--help
            Print this message and exit.

    -l|--loglevel debug|info|error
            Set loglevel

    -f|--logfile filename
            Save log to file

    --prop
            Call by post-revprop-change, update commit log of rev.

    --repo
            Local repository path.
    
    --rev
            Revision
    
    --user
            User name for sync with svn mirrors
    
    --password
            User password for sync with svn mirrors
    
    --urls
            Urls of downstream svn mirrors, seperate by `;'.
    
    -q|--quiet
            Quiet mode

    -v|--verbose
            Verbose mode
'''

import commands
import sys, os
import getopt
import re
import logging,logging.handlers
from subprocess import Popen, PIPE, STDOUT

program = sys.argv[0]
log = logging.getLogger('main')

SVNSYNCCMD = "LC_ALL=C svnsync --non-interactive --no-auth-cache --trust-server-cert "
SVNCMD     = "LC_ALL=C svn     --non-interactive --no-auth-cache --trust-server-cert "


class SVN_INFO(object):
    def __init__(self, url, username, password):
        self.url = None
        self.root = None
        self.uuid = None
        self.rev = None

        if username and password:
            command = SVNCMD + "info %(url)s --username %(username)s --password %(password)s" % locals()
        else:
            command = SVNCMD + "info %(url)s" % locals()
        proc = Popen( command, stdout=PIPE, stderr=STDOUT, close_fds=True, shell=True )
        output = proc.communicate()[0]
        if proc.returncode != 0:
            log.error("Failed when execute: %s\n\tgenerate warnings with returncode %d." % (self.strip_password(command), proc.returncode))
            if output:
                log.error( "Command output:\n" + output )
            raise Exception("Repository %(url)s can not access. Detail: %(output)s." % locals())

        self.parse(output)

    def parse(self, output):
        if output:
            if isinstance(output, (str, unicode)):
                output = output.splitlines()
            for line in output:
                if line.startswith("URL:"):
                    self.url = line.split(':',1)[1].strip()
                elif line.startswith("Repository Root:"):
                    self.root = line.split(':',1)[1].strip()
                elif line.startswith("Repository UUID:"):
                    self.uuid = line.split(':',1)[1].strip()
                elif line.startswith("Revision:"):
                    self.rev = line.split(':',1)[1].strip()


def parse_options(argv=None):
    try:
        opts, args = getopt.getopt( 
                argv, "hvqPR:r:u:p:U:l:f:", 
                ["help", "verbose", "quiet", "prop", "repo=", "rev=", "user=", "password=", "urls=", "loglevel=", "logfile="])
    except getopt.error, msg:
        return usage(1, msg)

    class Options: pass
    obj = Options()
    obj.repo = None
    obj.rev = None
    obj.urls = None
    obj.username = None
    obj.password = None
    obj.prop = False
    obj.loglevel = None
    obj.logfile = None
    obj.verbose = False

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            return usage()
        elif opt in ("-v", "--verbose"):
            obj.verbose = True
        elif opt in ("-q", "--quiet"):
            obj.verbose = False
        elif opt in ("-l", "--loglevel"):
            obj.loglevel = arg.lower()
        elif opt in ("-f", "--logfile"):
            obj.logfile = arg
        elif opt in ("-P", "--prop"):
            obj.prop = True
        elif opt in ("-R", "--repo"):
            obj.repo = arg
        elif opt in ("-r", "--rev"):
            obj.rev = arg
        elif opt in ("-u", "--user"):
            obj.username = arg
        elif opt in ("-p", "--password"):
            obj.password = arg
        elif opt in ("-U", "--urls"):
            obj.urls = arg
        else:
            return usage(1)

    loglevel = logging.WARNING
    if obj.loglevel == 'critical':
        loglevel = logging.CRITICAL
    elif obj.loglevel == 'info':
        loglevel = logging.INFO
    elif obj.loglevel in ('warning', 'warn'):
        loglevel = logging.WARNING
    elif obj.loglevel == 'error':
        loglevel = logging.ERROR
    elif obj.loglevel is not None:
        loglevel = logging.DEBUG

    log_format = "%(levelname)s : %(asctime)-15s > %(message)s"
    log_options = {}
    log_options['format'] = log_format
    log_options['level'] = loglevel
        
    logging.basicConfig(**log_options)

    # log to file
    if isinstance(obj.logfile, (str,unicode)):
        logger_f = logging.FileHandler(obj.logfile)
        logger_f.setLevel(loglevel)
        logger_f.setFormatter(logging.Formatter(log_format))
        # add file_logger to root logger
        logging.getLogger('').addHandler(logger_f)

    return obj


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
    if argv is None:
        argv = sys.argv[1:]

    try:
        opts = parse_options(argv)
        svnsync(opts.repo, opts.rev, opts.urls, opts.username,
                opts.password, opts.prop)
    except Exception, e:
        sys.stderr.write("error: %s\n" % str(e))
        sys.exit(1)

def svnsync(repo, rev, urls, username, password, prop):

    def get_lock_uuid(mirror, username, password):
        if username and password:
            extra_opt = " --username %(username)s --password %(password)s " % locals()
        else:
            extra_opt = " "
        command = SVNCMD + extra_opt + "pl --revprop -v -r0 %(mirror)s" % locals()

        proc = Popen( command, stdout=PIPE, stderr=STDOUT, close_fds=True, shell=True )
        output = proc.communicate()[0]
        lock_uuid = None
        if proc.returncode != 0:
            log.error( "Failed to get prop for revsion 0." )
            if output:
                log.error( "Command output:\n" + output )
            return None
        else:
            lines = output.splitlines()
            for i in range(len(lines)):
                if lines[i].lstrip().startswith( "svn:sync-lock" ):
                    lock_uuid = lines[i+1].strip().split(':',1)[1]
                    break
        return lock_uuid

    def rm_lock_uuid(mirror, username, password):
        if username and password:
            extra_opt = " --username %(username)s --password %(password)s " % locals()
        else:
            extra_opt = " "

        commands = []
        commands.append( SVNCMD + extra_opt + "pd svn:sync-lock --revprop -r0 %(mirror)s" % locals() )
        commands.append( SVNCMD + extra_opt + "pd svn:sync-currently-copying --revprop -r0 %(mirror)s" % locals() )
        for command in commands:
            proc = Popen( command, stdout=PIPE, stderr=STDOUT, close_fds=True, shell=True )
            output = proc.communicate()[0]
            if proc.returncode != 0:
                log.error( "Failed to remove sync lock from %s" % mirror )
                if output:
                    log.error( "Command output:\n" + output )
                return False

    def set_lock_pid(lockfile):
        f = open(lockfile, "w")
        f.write( str(os.getpid()) )
        f.close()

    def get_lock_pid(lockfile):
        if os.access(lockfile, os.R_OK):
            f = open(lockfile, "r")
            pid = f.readline().strip()
            f.close()
        else:
            pid = None
        return pid

    lockfile = os.path.join(repo, 'conf', 'svnsync.lock')
    sinfo = SVN_INFO("file://"+repo, username, password)

    for mirror in urls.split(";"):
        lock_uuid = get_lock_uuid(mirror, username, password)

        if lock_uuid:
            # lock_uuid not related with sinfo.uuid
            pid = get_lock_pid(lockfile)
            if pid:
                command = "ps -o cmd:1024 %s" % pid
                proc = Popen( command, stdout=PIPE, stderr=STDOUT, close_fds=True, shell=True )
                lines = proc.communicate()[0].splitlines()
                if len(lines) <2:
                    p_info = ""
                else:
                    p_info = lines[1].strip()

                if p_info:
                    p_cmd = p_info.split(None, 1)[0]
                    if os.path.basename(p_cmd) == "python":
                        p_cmd = p_info[len(p_cmd):].split(None, 1)[0]
                    p_cmd = os.path.basename(p_cmd)

                    if p_cmd == os.path.basename(__file__):
                        log.error( "Another svnsync process (%s:%s) is still working, please wait." % (pid, p_cmd) )
                        continue
                    else:
                        log.warning( "Svnsync is locked by process (%s:%s), but it seems not a real svn_mirror.py task." % (pid, p_cmd) )

            # remove svn:sync-lock from mirror.
            rm_lock_uuid(mirror, username, password)

        # write current pid to lockfile
        set_lock_pid(lockfile)

        mirror = mirror.strip()
        if username and password:
            extra_opt = " --sync-username %(username)s --sync-password %(password)s " % locals()
        else:
            extra_opt = " "
        if prop:
            command = SVNSYNCCMD + extra_opt + "copy-revprops %(mirror)s %(rev)s" % locals()
        else:
            command = SVNSYNCCMD + extra_opt + "sync %(mirror)s" % locals()

        proc = Popen( command, stdout=PIPE, stderr=STDOUT, close_fds=True, shell=True )

        output = proc.communicate()[0]
        if proc.returncode != 0:
            log.error( "Failed when execute: %s\n\tgenerate warnings with returncode %d." % (
                        prop and "svnsync copy-revprops" or "svnsync sync",
                        proc.returncode) )
            if output:
                log.error( "Command output:\n" + output )
        else:
            log.debug( "command: %s" % (prop and "svnsync copy-revprops" or "svnsync sync") )
            if output:
                log.debug( "output:\n" + output )
    
        # remove lockfile
        os.unlink( lockfile )


if __name__ == "__main__":
    sys.exit(main())

# vim:et:ts=4:sw=4
