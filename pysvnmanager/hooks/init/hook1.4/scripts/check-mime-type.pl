#!/usr/bin/perl -w

# ====================================================================
# commit-mime-type-check.pl: check that every added file has the
# svn:mime-type property set and every added file with a mime-type
# matching text/* also has svn:eol-style set. If any file fails this
# test the user is sent a verbose error message suggesting solutions and
# the commit is aborted.
#
# Usage: commit-mime-type-check.pl REPOS TXN-NAME
# ====================================================================
# Most of commit-mime-type-check.pl was taken from
# commit-access-control.pl, Revision 9986, 2004-06-14 16:29:22 -0400.
# ====================================================================
# Copyright (c) 2000-2004 CollabNet.  All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.  The terms
# are also available at http://subversion.tigris.org/license.html.
# If newer versions of this license are posted there, you may use a
# newer version instead, at your option.
#
# This software consists of voluntary contributions made by many
# individuals.  For exact contribution history, see the revision
# history and logs, available at http://subversion.tigris.org/.
# ====================================================================

# Turn on warnings the best way depending on the Perl version.
BEGIN {
  if ( $] >= 5.006_000)
    { require warnings; import warnings; }                      
  else  
    { $^W = 1; }               
}           

use strict;
use Carp;


######################################################################
# Configuration section.

# Svnlook path.
my $svnlook = "/usr/bin/svnlook";
$ENV{'LANG'} = 'zh_CN.UTF8';
$ENV{'LC_ALL'} = 'zh_CN.UTF8';

# Since the path to svnlook depends upon the local installation
# preferences, check that the required program exists to insure that
# the administrator has set up the script properly.
{
  my $ok = 1;
  foreach my $program ($svnlook)
    {
      if (-e $program)
        {
          unless (-x $program)
            {
              warn "$0: required program `$program' is not executable, ",
                   "edit $0.\n";
              $ok = 0;
            }
        }
      else
        {
          warn "$0: required program `$program' does not exist, edit $0.\n";
          $ok = 0;
        }
    }
  exit 1 unless $ok;
}

######################################################################
# Initial setup/command-line handling.

&usage unless @ARGV == 2;

my $repos        = shift;
my $txn          = shift;

unless (-e $repos)
  {
    &usage("$0: repository directory `$repos' does not exist.");
  }
unless (-d $repos)
  {
    &usage("$0: repository directory `$repos' is not a directory.");
  }

# Define two constant subroutines to stand for read-only or read-write
# access to the repository.
sub ACCESS_READ_ONLY  () { 'read-only' }
sub ACCESS_READ_WRITE () { 'read-write' }


######################################################################
# Harvest data using svnlook.

# Change into /tmp so that svnlook diff can create its .svnlook
# directory.
my $tmp_dir = '/tmp';
chdir($tmp_dir)
  or die "$0: cannot chdir `$tmp_dir': $!\n";

# Figure out what files have added using svnlook.
my @files_added;
foreach my $line (&read_from_process($svnlook, 'changed', $repos, '-t', $txn))
  {
		# Add only files that were added to @files_added
    if ($line =~ /^A.  (.*[^\/])$/)
      {
        push(@files_added, $1);
      }
  }

my @errors;
foreach my $path ( @files_added ) 
	{
		my $mime_type;
		my $eol_style;
		my $check_mime = 1;

		# Parse the complete list of property values of the file $path to extract
		# the mime-type and eol-style
		foreach my $prop (&read_from_process($svnlook, 'proplist', $repos, '-t', 
		                  $txn, '--verbose', $path))
			{
				if ($prop =~ /^\s*svn:mime-type : (\S+)/)
					{
						$mime_type = $1;
					}
				elsif ($prop =~ /^\s*svn:eol-style : (\S+)/)
					{
						$eol_style = $1;
					}
				elsif ($prop =~ /^\s*svn:special : (\S+)/)
					{
						$check_mime = 0;
					}
			}

		# Detect error conditions and add them to @errors
		if ($check_mime)
		{
			if (not $mime_type and not $eol_style)
				{
					push @errors, "$path : 属性 svn:mime-type 或者 svn:eol-style 没有设置";
				}
			elsif ($mime_type =~ /^text\// and not $eol_style)
				{
					push @errors, "$path : svn:mime-type=$mime_type 但是 svn:eol-style 没有设置";
				}
		}
	}

# If there are any errors list the problem files and give information
# on how to avoid the problem. Hopefully people will set up auto-props
# and will not see this verbose message more than once.
if (@errors)
  {
    warn "$0:\n\n",
         join("\n", @errors), "\n\n",
				 <<EOS;

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
    Automatic Property Setting subsection.
EOS
    exit 1;
  }
else
  {
    exit 0;
  }

sub usage
{
  warn "@_\n" if @_;
  die "usage: $0 REPOS TXN-NAME\n";
}

sub safe_read_from_pipe
{
  unless (@_)
    {
      croak "$0: safe_read_from_pipe passed no arguments.\n";
    }
  print "Running @_\n";
  my $pid = open(SAFE_READ, '-|');
  unless (defined $pid)
    {
      die "$0: cannot fork: $!\n";
    }
  unless ($pid)
    {
      open(STDERR, ">&STDOUT")
        or die "$0: cannot dup STDOUT: $!\n";
      exec(@_)
        or die "$0: cannot exec `@_': $!\n";
    }
  my @output;
  while (<SAFE_READ>)
    {
      chomp;
      push(@output, $_);
    }
  close(SAFE_READ);
  my $result = $?;
  my $exit   = $result >> 8;
  my $signal = $result & 127;
  my $cd     = $result & 128 ? "with core dump" : "";
  if ($signal or $cd)
    {
      warn "$0: pipe from `@_' failed $cd: exit=$exit signal=$signal\n";
    }
  if (wantarray)
    {
      return ($result, @output);
    }
  else
    {
      return $result;
    }
}

sub read_from_process
  {
  unless (@_)
    {
      croak "$0: read_from_process passed no arguments.\n";
    }
  my ($status, @output) = &safe_read_from_pipe(@_);
  if ($status)
    {
      if (@output)
        {
          die "$0: `@_' failed with this output:\n", join("\n", @output), "\n";
        }
      else
        {
          die "$0: `@_' failed with no output.\n";
        }
    }
  else
    {
      return @output;
    }
}
