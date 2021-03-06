��    �      \              �  �   �  J   A  �  �       >   9     x     |     �  D   �     �     �     �            #   '     K     R  	   ^     h     }  5   �  	   �  K   �  1        P     n     �     �     �  
   �     �     �     �  H        Z  $   h     �     �     �     �  �   �  �   {     9     A     S  ,   d     �  @   �  &   �          !     )     1     8     M     h  ,   �     �     �  L   �  2   *  @   ]     �     �  (   �     �     �     �               0     E     ^     w     �  
   �     �  )   �     �       #        +     2     7     :  #   K     o     �  }   �  �        �     �     �             
   !  S   ,     �     �     �     �     �     �  5   �     -     B     O     W  F   _     �  &   �     �     �  	   �  	          7        U  
   e     p          �  +   �  B   �           3      ?      F   	   S   5   ]   8   �   -   �      �   `   !     n!     !     �!     �!     �!  `   �!     B"     K"     T"     n"  !   �"  =   �"     �"     �"     #     ##     9#  #   R#     v#     �#  
   �#     �#     �#  ,   �#     $     !$     2$     >$     B$     R$     b$     k$  %   $     �$  (   �$  ^   �$     G%     L%     Y%  k   m%  "   �%  |   �%     y&  C   �&  (   �&     �&  X  '     f(     �(     �(     �(      �(  �   �(  p   �)  k   *     �*  4   �*  "   �*  !   �*     +     +     0+     A+     Y+     l+     �+     �+  9   �+     �+     ,     ,  5   >,  0   t,  3   �,  <   �,  /   -  2   F-  ?   y-  D   �-  H   �-     G.     Y.  2   l.  
   �.     �.  	   �.     �.     �.     �.     �.     �.     �.     �.     /  ,   /     E/     c/  �  y/  �   1  J   �1  �  �1     �4  >   �4     �4     �4     �4  D   �4     =5     L5     [5     h5     |5  #   �5     �5     �5  	   �5     �5     �5  5   �5  	   -6  K   76  1   �6     �6     �6     �6     7     '7  
   .7     97     K7     d7  H   v7     �7  $   �7     �7     �7     8     38  �   M8  �   �8     �9     �9     �9  ,   �9     �9  @   :  &   I:     p:     �:     �:     �:     �:     �:     �:  ,   �:     ;     ';  L   B;  2   �;  @   �;     <     
<  (   <     ?<     G<     ^<     t<     {<     �<     �<     �<     �<     �<  
   =     =  )   %=     O=     g=  #   l=     �=     �=     �=     �=  #   �=     �=     �=  }   �=  �   w>     ;?     G?     _?     e?     ?  
   �?  S   �?     �?     @     @     @     ;@     L@  5   \@     �@     �@     �@     �@  F   �@     A  &   A     7A     JA  	   ^A  	   hA     rA  7   �A     �A  
   �A     �A     �A     �A  +   B  B   <B     B     �B     �B     �B  	   �B  5   �B  8   �B  -   1C     _C  `   rC     �C     �C     �C     D     (D  `   FD     �D     �D     �D     �D  !   �D  =   E     LE     dE     vE     �E     �E  #   �E     �E     �E  
   
F     F     .F  ,   ?F     lF     �F     �F     �F     �F     �F     �F     �F  %   �F     
G  (   $G  ^   MG     �G     �G     �G  k   �G  "   >H  |   aH     �H  C   �H  (   .I     WI  X  rI     �J     �J     �J     K      #K  �   DK  p   
L  k   {L     �L  4   M  "   8M  !   [M     }M     �M     �M     �M     �M     �M     �M     �M  9   N     TN     iN     �N  5   �N  0   �N  3   
O  <   >O  /   {O  2   �O  ?   �O  D   P  H   cP     �P     �P  2   �P  
   Q     Q  	   Q     Q     %Q     <Q     SQ     [Q     `Q     dQ     hQ  ,   }Q     �Q     �Q   
%(heading)s
Access map on '%(repos)s' for user '%(user)s'
%(heading)s
  * Writable:
%(write)s
%(sep)s
  * Readable:
%(read)s
%(sep)s
  * Denied:
%(deny)s
%(sep)s
 
%(user)s => [%(repos)s]
%(sep)s
RW: %(write)s
RO: %(read)s
XX: %(deny)s

 
You must provide proper options to commit-email.pl using the
configuration form for this plugin.

You can simply just provide the email_addr as the options.

  [options] email_addr [email_addr ...]

But to be more versitile, you can setup a path-based email 
notifier.

  [-m regex1] [options] [email_addr ...]
  [-m regex2] [options] [email_addr ...] 
  ...

Options:

-m regex              Regular expression to match committed path
--from email_address  Email address for 'From:' (overrides -h)
-r email_address      Email address for 'Reply-To:
-s subject_prefix     Subject line prefix
--diff n              Do not include diff in message (default: y)
 %s is referenced by [%s]. A pre-commit hook to detect case-insensitive filename clashes. ACL ACL management Account Add %(add)d users, delete %(delete)d users, update %(update)d users. Add membership Add repository Admin user:  Administration logs Administrators: Alias %s is referenced by group %s. Alias: All modules All repos All users(with anon) Allow revprop change Allow user change commit-log or other rev-properties. Anonymous Apply plugin '%(plugin)s' on '%(repos)s' Failed. Error message:<br>
%(msg)s Apply plugin '%(plugin)s' on '%(repos)s' success. Are you sure to delete alias: Are you sure to delete group: Are you sure to delete module: Can not delete module  Cancel Change log Check Permissions Check commit log message Check permissions Check subversion client version. if version below 1.5.0, checkin denied. Clear message Click Ok to proceed, or click cancel Close Commit log check is disabled. Commit log check is enabled. Commit log size must > 0. Commit to the remote svn server, this repository is a readonly svn mirror.It is the svnsync admin's duty to synchronize svnsync server and mirror. Commit-log is the only rev-prop we allow to change. Because the changes of rev-prop can not be reverted back, administrator must setup email notification to record this irreversible action. Compare Compare revisions Compares between Conflict: plugin '%s' is modified by others. Create repository Create repository '%(repos)s' Failed. Error message:<br>
%(msg)s Create repository '%(repos)s' success. Current configuration Debug:  Default Delete Delete alias failed: Delete alias successfully. Delete blank repos: %s. Delete blank repository '%(repos)s' success. Delete group failed: Delete group successfully. Delete plugin '%(plugin)s' on '%(repos)s' Failed. Error message:<br>
%(msg)s Delete plugin '%(plugin)s' on '%(repos)s' success. Delete repository '%(repos)s' Failed. Error message:<br>
%(msg)s Denied Description Detect case-insensitive filename clashes Disable Email notify disabled. Email notify enabled. Enable Enable commit log check:  Enable email notify. Enable readonly mirror:  Enable svn repo mirror:  Enable trac post commit hook:  Error Traceback Exception: Fill this form Fixed ticket status (default is closed):  Fixed ticket's status:  Full Group %s is referenced by group %s. Group: Help Id Ignore recursive Input email notify configurations:  Install this plugin Installed hooks: Integrate subversion with trac: Commit log of subversion appends to trac tickets if subversion commit log contains ticket id. Integration Subversion with Mantis bugtracking. If commit-log has proper format (contains bugid), it will change bug status and append commint-log and code differ as comment of bug status change. Known users Loading, please wait... Login Login failed for user: %s Logout Loose mode Loose mode: permit checkin without svn:eol-style properity if no CRLF in text file. Mantis bugtracking integration Manual input Members list Minimal size of commit log:  Mirror disabled. Mirror enabled. Modified external, save to avoid configuration error. Module %s not exist. Module Path: Module: Modules Must set svn:eol-style even if CRLF not in text file (in Unix format). Name Name (%s) contains invalid characters. Name is not given. Name is not string. New Alias New Group New alias name: New file must provide svn:eol-style if not binary file. New group name: New module New repository No module exist for %s:%s No path selected. No plugin has been deleted for '%(repos)s'. No rights selected! Please check proper rights for selected users. Not a valid username: %s Other users Page:  Parameters:  Password: Pattern which commit log must **NOT** match against:  Pattern which commit log must <b>NOT</b> match against:  Pattern which commit log must match against:  Permission denied. Permit checkin without svn:eol-style properity if is in Unix file format (no crlf in text file). Please choose... Please input module path. Please input repository name. Plugin name Plugin not fully implemented. Powered by <a href="%(url1)s">pySvnManager</a> &copy; 2008-2010 <a href="%(url2)s">ossxp.com</a> ReadOnly Readonly Readonly mirror disabled. Readonly mirror enabled. Recursive group membership for %s Reload this page immediately, and show the update users list. Remove blank repository Remove membership Remove repository Remove selected hooks Repos %s already exists. Repos %s is not a blank repository. Repos management Repos root does not exist: %s Repository Repository %s not exist. Repository Name: Repository name in trac (default is blank):  Repository name in trac:  Repository name: Repository: Rev Role Management Role management Rollback Rollback failed: %s Rollback successfully to revision: %s Rollback to this revision Rollback to this revision, are you sure? SVN below 1.5.0 can not handle mergeinfo properly.It can mess up our automated merge tracking! Save Save failed. Select a role name: Send a notification email describing either a commit or a revprop-change action on a Subversion repository. Send email notify for commit event Some one maybe you, has modified the svn authz file by hands. Please %(begin)ssave once%(end)s to fix possible config error. Strict mode Strict mode: must have svn:eol-style even if not CRLF in text file. Subversion client version check (>1.5.0) Subversion readonly mirror Subversion services may host on a filename case-sensitive OS,
while client **may not** (Windows is case-insensitive). This may cause 'clash'.

- Detects new paths that 'clash' with existing, or other new, paths.
- Ignores existings paths that already 'clash'
- Exits with an error code, and a diagnostic on stderr, if 'clashes'
  are detected.
 Successfully delete module: Svnsync administrator:  Svnsync password: Svnsync username: Sync with downstream svn mirrors This master svn repository maybe configured with one or several svn mirrors.You must give the url svn mirrors (one with each line), and give the username and password who initiates the mirror task. This subversion repository is a svnsync master server. Each new commit will propagate to downstream svn mirrors. This subversion repository is a svnsync readonly mirror. Nobody can checkin, except the svnsync admin user. Trac environment location:  Trac integration with subversion's post commit hook. Trac post commit hook is disabled. Trac post commit hook is enabled. Type Uninstalled hooks: Unknown rights:  Unknown rule format: %s Update ACL failed: Update ACL successfully. Update alias failed: Update alias successfully. Update failed! You are working on a out-of-date revision. Update group failed: Update group successfully. Url of downstream svn mirrors: User %(user)s changed alias: %(alias)s. (rev:%(rev)s) User %(user)s changed authz rules. (rev:%(rev)s) User %(user)s changed group: %(grp)s. (rev:%(rev)s) User %(user)s delete alias: %(alias)s. (rev:%(rev)s,%(msg)s) User %(user)s delete authz rules. (rev:%(rev)s) User %(user)s delete group: %(grp)s. (rev:%(rev)s) User %(username)s can *NOT* access to module %(repos)s:%(path)s User %(username)s has Full (RW) rights for module %(repos)s:%(path)s User %(username)s has ReadOnly (RO) rights for module %(repos)s:%(path)s User %s logged in User %s logged out User must provide commit-log message when checkin. User name: User: Username: Users Users update from LDAP View history, revision Welcome When Who Why Wrong configuration. You can not delete yourself from admin list. mime-type and eol-style check repos '%s' not exist! Project-Id-Version: pysvnmanager 0.0.0
Report-Msgid-Bugs-To: EMAIL@ADDRESS
POT-Creation-Date: 2011-07-04 18:04+0800
PO-Revision-Date: 2009-11-10 14:23+0800
Last-Translator: Jiang Xin <jiangxin@ossxp.com>
Language-Team: en <LL@li.org>
Plural-Forms: nplurals=2; plural=(n != 1)
MIME-Version: 1.0
Content-Type: text/plain; charset=utf-8
Content-Transfer-Encoding: 8bit
Generated-By: Babel 0.9.6
 
%(heading)s
Access map on '%(repos)s' for user '%(user)s'
%(heading)s
  * Writable:
%(write)s
%(sep)s
  * Readable:
%(read)s
%(sep)s
  * Denied:
%(deny)s
%(sep)s
 
%(user)s => [%(repos)s]
%(sep)s
RW: %(write)s
RO: %(read)s
XX: %(deny)s

 
You must provide proper options to commit-email.pl using the
configuration form for this plugin.

You can simply just provide the email_addr as the options.

  [options] email_addr [email_addr ...]

But to be more versitile, you can setup a path-based email 
notifier.

  [-m regex1] [options] [email_addr ...]
  [-m regex2] [options] [email_addr ...] 
  ...

Options:

-m regex              Regular expression to match committed path
--from email_address  Email address for 'From:' (overrides -h)
-r email_address      Email address for 'Reply-To:
-s subject_prefix     Subject line prefix
--diff n              Do not include diff in message (default: y)
 %s is referenced by [%s]. A pre-commit hook to detect case-insensitive filename clashes. ACL ACL management Account Add %(add)d users, delete %(delete)d users, update %(update)d users. Add membership Add repository Admin user:  Administration logs Administrators: Alias %s is referenced by group %s. Alias: All modules All repos All users(with anon) Allow revprop change Allow user change commit-log or other rev-properties. Anonymous Apply plugin '%(plugin)s' on '%(repos)s' Failed. Error message:<br>
%(msg)s Apply plugin '%(plugin)s' on '%(repos)s' success. Are you sure to delete alias: Are you sure to delete group: Are you sure to delete module: Can not delete module  Cancel Change log Check Permissions Check commit log message Check permissions Check subversion client version. if version below 1.5.0, checkin denied. Clear message Click Ok to proceed, or click cancel Close Commit log check is disabled. Commit log check is enabled. Commit log size must > 0. Commit to the remote svn server, this repository is a readonly svn mirror.It is the svnsync admin's duty to synchronize svnsync server and mirror. Commit-log is the only rev-prop we allow to change. Because the changes of rev-prop can not be reverted back, administrator must setup email notification to record this irreversible action. Compare Compare revisions Compares between Conflict: plugin '%s' is modified by others. Create repository Create repository '%(repos)s' Failed. Error message:<br>
%(msg)s Create repository '%(repos)s' success. Current configuration Debug:  Default Delete Delete alias failed: Delete alias successfully. Delete blank repos: %s. Delete blank repository '%(repos)s' success. Delete group failed: Delete group successfully. Delete plugin '%(plugin)s' on '%(repos)s' Failed. Error message:<br>
%(msg)s Delete plugin '%(plugin)s' on '%(repos)s' success. Delete repository '%(repos)s' Failed. Error message:<br>
%(msg)s Denied Description Detect case-insensitive filename clashes Disable Email notify disabled. Email notify enabled. Enable Enable commit log check:  Enable email notify. Enable readonly mirror:  Enable svn repo mirror:  Enable trac post commit hook:  Error Traceback Exception: Fill this form Fixed ticket status (default is closed):  Fixed ticket's status:  Full Group %s is referenced by group %s. Group: Help Id Ignore recursive Input email notify configurations:  Install this plugin Installed hooks: Integrate subversion with trac: Commit log of subversion appends to trac tickets if subversion commit log contains ticket id. Integration Subversion with Mantis bugtracking. If commit-log has proper format (contains bugid), it will change bug status and append commint-log and code differ as comment of bug status change. Known users Loading, please wait... Login Login failed for user: %s Logout Loose mode Loose mode: permit checkin without svn:eol-style properity if no CRLF in text file. Mantis bugtracking integration Manual input Members list Minimal size of commit log:  Mirror disabled. Mirror enabled. Modified external, save to avoid configuration error. Module %s not exist. Module Path: Module: Modules Must set svn:eol-style even if CRLF not in text file (in Unix format). Name Name (%s) contains invalid characters. Name is not given. Name is not string. New Alias New Group New alias name: New file must provide svn:eol-style if not binary file. New group name: New module New repository No module exist for %s:%s No path selected. No plugin has been deleted for '%(repos)s'. No rights selected! Please check proper rights for selected users. Not a valid username: %s Other users Page:  Parameters:  Password: Pattern which commit log must **NOT** match against:  Pattern which commit log must <b>NOT</b> match against:  Pattern which commit log must match against:  Permission denied. Permit checkin without svn:eol-style properity if is in Unix file format (no crlf in text file). Please choose... Please input module path. Please input repository name. Plugin name Plugin not fully implemented. Powered by <a href="%(url1)s">pySvnManager</a> &copy; 2008-2010 <a href="%(url2)s">ossxp.com</a> ReadOnly Readonly Readonly mirror disabled. Readonly mirror enabled. Recursive group membership for %s Reload this page immediately, and show the update users list. Remove blank repository Remove membership Remove repository Remove selected hooks Repos %s already exists. Repos %s is not a blank repository. Repos management Repos root does not exist: %s Repository Repository %s not exist. Repository Name: Repository name in trac (default is blank):  Repository name in trac:  Repository name: Repository: Rev Role Management Role management Rollback Rollback failed: %s Rollback successfully to revision: %s Rollback to this revision Rollback to this revision, are you sure? SVN below 1.5.0 can not handle mergeinfo properly.It can mess up our automated merge tracking! Save Save failed. Select a role name: Send a notification email describing either a commit or a revprop-change action on a Subversion repository. Send email notify for commit event Some one maybe you, has modified the svn authz file by hands. Please %(begin)ssave once%(end)s to fix possible config error. Strict mode Strict mode: must have svn:eol-style even if not CRLF in text file. Subversion client version check (>1.5.0) Subversion readonly mirror Subversion services may host on a filename case-sensitive OS,
while client **may not** (Windows is case-insensitive). This may cause 'clash'.

- Detects new paths that 'clash' with existing, or other new, paths.
- Ignores existings paths that already 'clash'
- Exits with an error code, and a diagnostic on stderr, if 'clashes'
  are detected.
 Successfully delete module: Svnsync administrator:  Svnsync password: Svnsync username: Sync with downstream svn mirrors This master svn repository maybe configured with one or several svn mirrors.You must give the url svn mirrors (one with each line), and give the username and password who initiates the mirror task. This subversion repository is a svnsync master server. Each new commit will propagate to downstream svn mirrors. This subversion repository is a svnsync readonly mirror. Nobody can checkin, except the svnsync admin user. Trac environment location:  Trac integration with subversion's post commit hook. Trac post commit hook is disabled. Trac post commit hook is enabled. Type Uninstalled hooks: Unknown rights:  Unknown rule format: %s Update ACL failed: Update ACL successfully. Update alias failed: Update alias successfully. Update failed! You are working on a out-of-date revision. Update group failed: Update group successfully. Url of downstream svn mirrors: User %(user)s changed alias: %(alias)s. (rev:%(rev)s) User %(user)s changed authz rules. (rev:%(rev)s) User %(user)s changed group: %(grp)s. (rev:%(rev)s) User %(user)s delete alias: %(alias)s. (rev:%(rev)s,%(msg)s) User %(user)s delete authz rules. (rev:%(rev)s) User %(user)s delete group: %(grp)s. (rev:%(rev)s) User %(username)s can *NOT* access to module %(repos)s:%(path)s User %(username)s has Full (RW) rights for module %(repos)s:%(path)s User %(username)s has ReadOnly (RO) rights for module %(repos)s:%(path)s User %s logged in User %s logged out User must provide commit-log message when checkin. User name: User: Username: Users Users update from LDAP View history, revision Welcome When Who Why Wrong configuration. You can not delete yourself from admin list. mime-type and eol-style check repos '%s' not exist! 