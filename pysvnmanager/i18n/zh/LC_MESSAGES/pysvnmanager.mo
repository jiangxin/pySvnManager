��    �      \              �  �   �  J   A  �  �       >   9     x     |     �  D   �     �     �     �            #   '     K     R  	   ^     h     }  5   �  	   �  K   �  1        P     n     �     �     �  
   �     �     �     �  H        Z  $   h     �     �     �     �  �   �  �   {     9     A     S  ,   d     �  @   �  &   �          !     )     1     8     M     h  ,   �     �     �  L   �  2   *  @   ]     �     �  (   �     �     �     �               0     E     ^     w     �  
   �     �  )   �     �       #        +     2     7     :  #   K     o     �  }   �  �        �     �     �             
   !  S   ,     �     �     �     �     �     �  5   �     -     B     O     W  F   _     �  &   �     �     �  	   �  	          7        U  
   e     p          �  +   �  B   �           3      ?      F   	   S   5   ]   8   �   -   �      �   `   !     n!     !     �!     �!     �!  `   �!     B"     K"     T"     n"  !   �"  =   �"     �"     �"     #     ##     9#  #   R#     v#     �#  
   �#     �#     �#  ,   �#     $     !$     2$     >$     B$     R$     b$     k$  %   $     �$  (   �$  ^   �$     G%     L%     Y%  k   m%  "   �%  |   �%     y&  C   �&  (   �&     �&  X  '     f(     �(     �(     �(      �(  �   �(  p   �)  k   *     �*  4   �*  "   �*  !   �*     +     +     0+     A+     Y+     l+     �+     �+  9   �+     �+     ,     ,  5   >,  0   t,  3   �,  <   �,  /   -  2   F-  ?   y-  D   �-  H   �-     G.     Y.  2   l.  
   �.     �.  	   �.     �.     �.     �.     �.     �.     �.     �.     /  ,   /     E/     c/  �  y/  �   1  V   �1  O  #2     s4  T   �4     �4     �4     �4  _   �4     \5     i5     y5     �5  
   �5  #   �5     �5     �5     �5     �5     �5  -   6     E6  S   R6  9   �6     �6     �6     7     17     E7     L7     Y7     f7     y7  Z   �7     �7  %   �7     8  !   8  !   =8  0   _8  �   �8  �   $9     :     :     ):  +   9:     e:  >   u:  #   �:     �:     �:     �:     �:     �:     ;     ';  #   A;     e;     ~;  S   �;  8   �;  >   $<     c<     j<  '   q<     �<     �<     �<     �<     �<     �<     =     =     9=     U=  	   c=     m=  4   z=      �=     �=      �=     �=     >     >     >  "   )>     L>     \>  �   o>  �   ?     �?     @     #@     *@     D@     K@  d   X@      �@     �@     �@  $   �@     A     -A  <   =A     zA     �A     �A     �A  h   �A     B  "   B     AB     WB  	   mB     wB     �B  0   �B     �B  	   �B     �B     �B     C  )   C  6   EC     |C     �C     �C     �C     �C  -   �C  .   �C  '   D     <D  |   LD     �D     �D     �D     E     E  b   1E     �E     �E     �E     �E     �E  6   �E     $F     7F     DF     TF     jF  +   �F     �F     �F  	   �F     �F     G  2   G      FG     gG  
   zG     �G     �G     �G     �G     �G     �G     �G  '   �G  j   H     �H     �H     �H  W   �H  $   I  �   ,I     �I  c   �I  )   8J     bJ  �  sJ     �K     L     %L     DL  $   `L  �   �L  s   yM  k   �M     YN     lN      �N      �N     �N     �N     �N     �N     O     O     1O     GO  T   ]O     �O     �O     �O  7    P  5   8P  8   nP  ?   �P  5   �P  8   Q  K   VQ  H   �Q  H   �Q     4R     ER  6   VR  
   �R     �R  
   �R     �R     �R     �R     �R     �R  	   �R     �R     �R  0   S  $   <S     aS   
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
 Successfully delete module: Svnsync administrator:  Svnsync password: Svnsync username: Sync with downstream svn mirrors This master svn repository maybe configured with one or several svn mirrors.You must give the url svn mirrors (one with each line), and give the username and password who initiates the mirror task. This subversion repository is a svnsync master server. Each new commit will propagate to downstream svn mirrors. This subversion repository is a svnsync readonly mirror. Nobody can checkin, except the svnsync admin user. Trac environment location:  Trac integration with subversion's post commit hook. Trac post commit hook is disabled. Trac post commit hook is enabled. Type Uninstalled hooks: Unknown rights:  Unknown rule format: %s Update ACL failed: Update ACL successfully. Update alias failed: Update alias successfully. Update failed! You are working on a out-of-date revision. Update group failed: Update group successfully. Url of downstream svn mirrors: User %(user)s changed alias: %(alias)s. (rev:%(rev)s) User %(user)s changed authz rules. (rev:%(rev)s) User %(user)s changed group: %(grp)s. (rev:%(rev)s) User %(user)s delete alias: %(alias)s. (rev:%(rev)s,%(msg)s) User %(user)s delete authz rules. (rev:%(rev)s) User %(user)s delete group: %(grp)s. (rev:%(rev)s) User %(username)s can *NOT* access to module %(repos)s:%(path)s User %(username)s has Full (RW) rights for module %(repos)s:%(path)s User %(username)s has ReadOnly (RO) rights for module %(repos)s:%(path)s User %s logged in User %s logged out User must provide commit-log message when checkin. User name: User: Username: Users Users update from LDAP View history, revision Welcome When Who Why Wrong configuration. You can not delete yourself from admin list. mime-type and eol-style check repos '%s' not exist! Project-Id-Version:  pysvnmanager
Report-Msgid-Bugs-To: EMAIL@ADDRESS
POT-Creation-Date: 2011-07-04 18:04+0800
PO-Revision-Date: 2010-08-26 20:18+0800
Last-Translator: Jiang Xin <worldhello.net@gmail.com>
Language-Team: Chinese Simplified <kde-i18n-doc@kde.org>
Plural-Forms: nplurals=2; plural=(n != 1)
MIME-Version: 1.0
Content-Type: text/plain; charset=utf-8
Content-Transfer-Encoding: 8bit
Generated-By: Babel 0.9.6
 
%(heading)s
用户 %(user)s 对版本库 [%(repos)s] 的访问权限为
%(heading)s
  * 读写:
%(write)s
%(sep)s
  * 只读:
%(read)s
%(sep)s
  * 禁用:
%(deny)s
%(sep)s
 
%(user)s => [%(repos)s]
%(sep)s
读写: %(write)s
只读: %(read)s
禁用: %(deny)s

 
您需要为代码变更的邮件通知设置参数。

可以简单的提供邮件地址即可：

  [options] email_addr [email_addr ...]

或者基于正则表达式，提供一个基于路径的代码变更的邮件通知。

  [-m regex1] [options] [email_addr ...]
  [-m regex2] [options] [email_addr ...] 
  ...

参数：

-m regex              和提交路径相匹配的正则表达式
--from email_address  发信人地址
-r email_address      回复邮件地址
-s subject_prefix     标题的前缀，如 [Prefix]
--diff n              不包含代码差异（缺省包含）
 %s 在 [%s] 中被引用。 在 pre-commit 钩子中执行，检查文件名大小写引起的文件名冲突。 ACL 权限控制 帐号 %(add)d 个用户被添加， %(delete)d 个用户被删除， %(update)d 个用户被更新。 添加成员 添加版本库 管理员:  修改记录 管理员: 别名 %s 为用户组 %s 引用。 别名: 所有模组 所有版本库 所有用户(含匿名) 允许修改版本属性 允许用户修改提交说明等版本属性 匿名用户 启用版本库'%(repos)s'的插件'%(plugin)s'失败。错误信息：<br>
%(msg)s 成功启用版本库'%(repos)s'的插件'%(plugin)s'。  您确认要删除别名: 您确认要删除用户组: 您确认要删除模组: 无法删除模组  取消 修改日志 权限检查 检查提交说明 权限检查 检查 subversion 客户端版本。如果版本号小于 1.5.0，禁止客户端提交。 清除消息 点击 OK 继续，或者点击取消 关闭 提交说明检查已经禁用。 提交说明检查已经启用。 提交说明最小长度阈值必须大于零。 提交到远程的 SVN 服务器，本地服务器是一个只读的 SVN 镜像。同步远程与本地的 SVN 服务器，是管理员的职责。 提交说明是我们唯一允许修改的版本属性。因为版本属性本身未被版本控制，修改版本属性是不可恢复的操作，所以管理员在启用本功能前，应该考虑设置变更通知以记录修改事件。 比较 版本比较 版本间比较 冲突：插件'%s'被其他人修改了。 创建版本库 创建版本库'%(repos)s'失败。错误信息：<br>
%(msg)s 成功创建版本库'%(repos)s'。 当前设置 Debug:  缺省 删除 删除别名失败： 成功删除别名。 删除空版本库: %s。 成功删除版本库'%(repos)s'。 更新用户组失败： 成功删除用户组。 删除版本库'%(repos)s'的插件'%(plugin)s'失败。错误信息：<br>
%(msg)s 成功删除版本库'%(repos)s'的插件'%(plugin)s'。 删除版本库'%(repos)s'失败。错误信息：<br>
%(msg)s 禁用 说明 检查大小写引起的文件名冲突 关闭 邮件通知关闭。 邮件通知启用。 启用 启用提交说明检查： 启用邮件通知。 启用只读镜像： 启用 SVN 版本库镜像： 启用 trac 整合插件： 错误跟踪: 异常： 填写表单 标记为修复的 ticket 状态 (缺省为 closed): 标记为修复的ticket状态:  完全权限 用户组 %s 被组 %s 引用。 团队: 帮助 Id 忽略组间循环引用 输入邮件通知配置参数：  安装此插件 已安装插件： 整合 SVN 与 trac： 如果 subversion 的提交说明包含 ticket id，则更新对应 trac 实例的 ticket 状态，将提交说明附加到 ticket 后。 与 Mantis 缺陷跟踪系统整合。当提交日志符合特定的规范（包含 bugid），将会触发 Mantis 缺陷跟踪系统，将 bug 的状态修改为已修改，并将commit-log 以及代码变更添加到说明中。 注册用户 数据加载中，请稍后... 登录 以 %s 身份登录失败 登出 宽松模式 宽松模式： 当提交的文本文件为 Unix 格式时，可以不提供 svn:eol-style 属性。 整合 Mantis 缺陷跟踪系统 手工输入 成员列表 提交说明长度检查，最少： 镜像禁用。 镜像启用。 来自外部的修改，重新保存以避免配置错误。 模组 %s 不存在。 模组路径: 模组: 模组 必须提供 svn:eol-style 属性，即使提交的文本文件内容中不包含CRLF（Unix格式）。 名称 名称(%s)中包含非法字符。 未能提供名称。 名称不是字符串 新别名 新用户组 新别名名称: 新增的文本文件，必须设置换行符。 新用户组名称: 新模组 新版本库 模块不存在: %s:%s 未选择路径。 未删除版本库'%(repos)s'的插件。 未选择权限！请为用户选择合适的权限。 非法用户名: %s 其他用户 页面:  参数:  口令: 提交说明 **不能** 出现类似内容： 提交说明<b>不能</b>出现类似内容： 提交说明必须与该模板匹配： 没有权限。 当提交的文本文件为 Unix 格式时（文本文件内容中不包含CRLF），可以不提供 svn:eol-style 属性。 请选择... 请输入模组路径。 请输入版本库名称。 插件名称 插件未完全实现。 基于 <a href="%(url1)s">pySvnManager</a> &copy; 2008-2010 <a href="%(url2)s">北京群英汇</a> 只读 只读 只读镜像关闭。 只读镜像启用。 %s 出现了循环组引用。 涮新本页面，以便显示更新的用户列表。 删除空版本库 移除成员 删除版本库 删除选择的插件 版本库 %s 已经存在。 版本库 %s 不是一个空的版本库。 版本库管理 版本库根不存在：%s 版本库 版本库 %s 不存在。 版本库名称: 此版本库 trac 中的名称（缺省为空）:  此版本库 trac 中的名称:  版本库名称： 版本库: 版本 角色管理 角色管理 数据回滚 回滚失败: %s 成功回滚至版本: %s 回滚至此版本 你确认回滚文件至此版本么？ 小于 1.5.0 版本的 SVN 客户端不能正确处理 mergeinfo。会破坏自动的合并追踪功能！ 保存 保存失败。 选择一个角色: 当对 Subversion 代码库中的代码修改或者修改状态，发出邮件通知。 针对代码变更发出邮件通知 有人可能是您，手工修改了 svn 授权文件，这可能导致 svn 不能工作。请  %(begin)s保存一次%(end)s，以修正可能的错误。 严谨模式 严谨模式： 必须提供 svn:eol-style 属性，即使提交的文本文件中不包含 CRLF。 Subversion 客户端版本检查 (>1.5.0) SVN 只读镜像 Subversion 服务可能安装在一个文件名大小写敏感的操作系统（如 Linux），
而客户端则可能 **不是** （Windows 文件名大小写不敏感）。这将造成冲突。

- 检查新提交的文件的路径是否和已经存在的路径或者其他新增文件相冲突。
- 忽略已经存在的“冲突”的路径
- 如果发现冲突，拒绝提交，并报错。
 成功删除模组: Svnsync 管理员: 发起同步的用户口令： 发起同步的用户名： 同步到下游的SVN镜像服务器 此 SVN 主版本库可以配置一个或多个下游的 SVN 镜像版本库。 您必须提供下游 SVN 镜像的 URL（每个一行），并且还要提供 发起同步的用户名和口令。此用户要对下游版本库具有写权限。 本 SVN 版本库是一个 svnsync 的主版本库。每一个提交都会同步给下游的 SVN 镜像版本库。 本 SVN 版本库是一个 svnsync 的只读镜像。除了 svnsync 管理员，任何人都不能提交。 Trac 环境路径: Trac 与 SVN 整合。 Trac 整合插件已经禁用。 Trac 整合插件已经启用。 类型 尚未安装的插件： 未知权限:  未知策略格式: %s 更新ACL失败： 成功更新ACL。 更新别名失败： 成功更新别名。 更新失败！您的更改是基于一个过期的版本，请先刷新再更改。 更新用户组失败： 成功更新用户组。 下游 SVN 镜像的 URL： 用户 %(user)s 修改别名: %(alias)s。(rev:%(rev)s) 用户 %(user)s 修改了授权策略。(rev:%(rev)s) 用户 %(user)s 修改用户组: %(grp)s。(rev:%(rev)s) 用户 %(user)s 删除别名: %(alias)s。(rev:%(rev)s,%(msg)s) 用户 %(user)s 删除了授权策略。(rev:%(rev)s) 用户 %(user)s 删除用户组: %(grp)s。(rev:%(rev)s) 用户 %(username)s 对模组 %(repos)s:%(path)s *没有* 访问权限 (XX) 用户 %(username)s 对模组 %(repos)s:%(path)s 具有完全权限 (RW) 用户 %(username)s 对模组 %(repos)s:%(path)s 具有只读权限 (RO) 用户 %s 登录 用户 %s 登出 用户在代码提交时，必须提供提交说明。 用户名: 用户: 用户名: 用户 和LDAP用户同步 查看历史, 版本 欢迎, 时间 管理员 说明 错误的配置 您不能将自己从管理员列表中删除。 文件类型和换行符设置检查 版本库 %s 不存在！ 