#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
check-mime-type.py: check that every added file has the
svn:mime-type property set and every added file with a mime-type
matching text/* also has svn:eol-style set. If any file fails this
test the user is sent a verbose error message suggesting solutions and
the commit is aborted.

Usage: commit-mime-type-check.pl REPOS TXN-NAME

Rewrite from check-mime-type.pl, by Jiang Xin<WorldHello.net.AT.gmail.com>
"""

__revision__ = '$Id: commit_log_check.py 513 2006-05-06 17:12:03Z jiangxin $'

import sys, os, re, string, locale

if os.name == 'nt':
    SVNLOOK = 'C:/Apps/Subversion/bin/svnlook.exe'
else:
    SVNLOOK = '/usr/bin/svnlook'

os.environ['LANG'] = os.environ['LC_ALL'] = 'zh_CN.UTF8'

MIN_LENGTH = 5

def main(repos, txn, force=""):
    """main entry point"""
    
    if force == "no":
        force = False 
    else:
        force = True

    files_added = []
    cmd = '%s changed -t "%s" "%s"' % (SVNLOOK, txn, repos)
    padd = re.compile(r'^A.  (.*[^/])$')

    for line in os.popen(cmd, 'r').readlines():
        match = padd.match( line.rstrip("\n") );
        if match:
            groups = match.groups()
            if len(groups) == 1:
                files_added.append( groups[0] );

    pmime = re.compile(r'\s*svn:mime-type : (\S+)')
    peol  = re.compile(r'\s*svn:eol-style : (\S+)')
    ptext = re.compile(r'^text/')
    pspecial = re.compile(r'\s*svn:special : (\S+)')
    
    errmsg = []
    for path in files_added:
        cmd = '%s proplist -t "%s" "%s" --verbose "%s"' % (SVNLOOK, txn, repos, path)
        mime_type = ''
        eol_style = ''
        check_mime = True
        
        for line in os.popen(cmd, 'r').readlines():
            if pmime.match(line):
                mime_type = pmime.match(line).group(1)
            elif pspecial.match(line):
                check_mime = False
            if peol.match(line):
                eol_style = peol.match(line).group(1)
        
        if check_mime:
            if mime_type == "" or ptext.match(mime_type):
                if eol_style == '':
                    ## check if crlf in file contents
                    if not force:
                        if crlf_in_file(txn, repos, path):
                            errmsg.append( "CRLF (DOS style EOL) in file: %s" % path.decode('utf-8','replace').encode('utf-8','replace') )
                        else:
                            continue
                    if mime_type == "":
                        errmsg.append( "%s : 属性 svn:mime-type 或者 svn:eol-style 没有设置" % path.decode('utf-8','replace').encode('utf-8','replace') )
                    else:
                        errmsg.append( "%s : svn:mime-type=%s 但是 svn:eol-style 没有设置" % (path.decode('utf-8','replace').encode('utf-8','replace'), mime_type) )

    if len( errmsg ) > 0:
        die( errmsg )

def crlf_in_file(txn, repos, path):
    cmd = '%s cat -t "%s" "%s" "%s"' % (SVNLOOK, txn, repos, path)
    buff = os.popen(cmd, 'r').read(1024)
    if '\r' in buff:
        return True
    else:
        return False
 
def die(msg):
    """
    Write verbose mesage, and exit
    """

    sys.stderr.write( "\n%s\n" % ("="*20) )
    sys.stderr.write( string.join(msg, '\n') )
    sys.stderr.write( "\n%s\n" % ("="*20) )
    
    sys.stderr.write("""\n
管理员已经启用换行符属性检查。每一个新添加的文件必须
指定换行符。如果 svn:mime-type 属性为文本文件，则
必须设置 svn:eol-style 属性。

对于二进制文件，执行如下命令：
svn propset svn:mime-type application/octet-stream path/of/file

对于文本文件，可以执行如下命令：
svn propset svn:mime-type text/plain path/of/file
svn propset svn:eol-style native path/of/file

为了避免每次添加文件手动设置，可以启用自动属性设置。
需要修改文件 ~/.subversion/config (Unix平台)。
打开 auto-props 设置，并设置扩展名和属性的对应关系。
详细设置，参见 Subversion 参考:
(http://svnbook.red-bean.com/), Chapter 7, Properties section,
Automatic Property Setting subsection.""")
    
    sys.exit(1)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.stderr.write("Usage: %s REPOS TXN\n" % (sys.argv[0]))
    else:
        main(sys.argv[1], sys.argv[2], sys.argv[3:] and sys.argv[3] or '')
