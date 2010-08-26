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
    commands = []
    for mirror in urls.split(";"):
        mirror = mirror.strip()
        commands.append( "svnsync sync %(mirror)s --sync-username %(username)s --sync-password %(password)s" % locals() )

    for command in commands:
        proc = Popen( command, stdout=PIPE, stderr=STDOUT, close_fds=True, shell=True )

        output = proc.communicate()[0]
        if proc.returncode != 0:
            log.error("Failed when execute: %s\n\tgenerate warnings with returncode %d." % (command, proc.returncode))
            if output:
                log.error( "Command output:\n" + output )
        else:
            log.debug( "command: %s" % command )
            if output:
                log.debug( "output:\n" + output )
    

if __name__ == "__main__":
    sys.exit(main())

# vim:et:ts=4:sw=4
