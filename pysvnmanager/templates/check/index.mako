## -*- coding: utf-8 -*-
## vim: et ts=4 sw=4
<%inherit file="/base.mako" />

<%def name="head_tags()">
    <title>${_("Check Permissions")}</title>
</%def>

<%
userlist = [('...', _("Please choose...")),
            ('*', _("All users(with anon)")),
            ('$authenticated', _("Known users")),
            ('$anonymous', _("Anonymous")),]
for id, display in c.userlist:
    if id == '*' or id =='$authenticated' or id == '$anonymous':
        continue
    if id[0] == '@':
        userlist.append((id, _("Group:")+id[1:]))
    elif id[0] == '&':
        userlist.append((id, _("Alias:")+id[1:]))
    elif display:
        userlist.append([id, "%s (%s)" % (id, display)])
    else:
        userlist.append([id, id])

reposlist = [('...', _("Please choose...")), ('*', _("All repos"))]
if '/' in c.reposlist:
    reposlist.append(('/', _("Default")))
for i in c.reposlist:
    if i == '/':
        continue
    reposlist.append((i, i))

pathlist = [[_("All modules"), '*'],]
for i in c.pathlist:
    pathlist.append([i, i])
%>

<SCRIPT LANGUAGE="JavaScript">
function edit_username(form)
{
    form.userinput[1].checked = true;
}
function select_username(form)
{
    form.userinput[0].checked = true;
}
function edit_repos(form)
{
    form.reposinput[1].checked = true;
}
function select_repos(form)
{
    form.reposinput[0].checked = true;
}
function edit_path(form)
{
    form.pathinput[1].checked = true;
}
function select_path(form)
{
    form.pathinput[0].checked = true;
}
function update_path(form)
{
    var repos = "";
    if (form.reposinput[0].checked) {
        repos = form.reposselector.options[form.reposselector.selectedIndex].value;
    } else {
        repos = form.reposname.value;
    }
    var params = {repos:repos};
    showNoticesPopup();
    new Ajax.Request(
        '${h.url(controller="check", action="get_auth_path")}',
        {asynchronous:true, evalScripts:true, method:'post',
            onComplete:
                function(request)
                    {hideNoticesPopup();ajax_update_path(request.responseText);},
            parameters:params
        });
}
function ajax_update_path(code)
{
    var id = new Array();
    var name = new Array();
    var total = 0;

    pathselector = document.forms[0].pathselector;
    lastselect = pathselector.value;
    pathselector.options.length = 0;

    try {
        eval(code);
        for (var i=0; i < total; i++)
        {
            pathselector.options[i] = new Option(name[i], id[i]);
            if (id[i]==lastselect)
                pathselector.options[i].selected = true;
        }
    }
    catch(exception) {
        alert(exception);
    }
}

</SCRIPT>

<h2>${_("Check Permissions")}</h2>

## Classic Form
##     ${h.form(h.url(controller="check", action='permission'), method='post')}

## AJAX Form

<form action="${h.url(controller='check', action='access_map')}"
  id="main_form" method="POST"
  onsubmit="showNoticesPopup();
            new Ajax.Updater({success:'acl_msg',failure:'message'},
                             '${h.url(controller='check', action='access_map')}',
                             {asynchronous:true, evalScripts:true, method:'post',
                              onComplete:function(request){hideNoticesPopup();new Effect.Highlight('acl_msg',{duration:1});},
                              parameters:Form.serialize(this)});
            return false;">

<table class="list">
<tr>
    <th>${_("Account")}</th>
    <th>${_("Repository")}</th>
    <th>${_("Modules")}</th>
</tr>

<tr>
    <td>
        <input type="radio" name="userinput" value="select" Checked>
            ${h.select("userselector", c.selected_username, userlist, onFocus="select_username(this.form)", Class="select-fix1")}
            <br/>
        <input type="radio" name="userinput" value="manual">
            ${_("Manual input")}
            <input type="text" name="username" size=15 maxlength=80 value="${c.typed_username}"
                onFocus="edit_username(this.form)" class="input-fix1">
    </td>

    <td>
        <input type="radio" name="reposinput" value="select" Checked onClick="update_path(this.form)">
            ${h.select("reposselector", c.selected_repos, reposlist, onFocus="select_repos(this.form)", onChange="update_path(this.form)", Class="select-fix1")}
            <br/>
        <input type="radio" name="reposinput" value="manual">
            ${_("Manual input")}
            <input type="text" name="reposname" size=15 value="${c.typed_repos}"
                onFocus="edit_repos(this.form)"
                onBlur="update_path(this.form)"
                class="input-fix1">
    </td>

    <td>
        <input type="radio" name="pathinput" value="select" Checked>
            <select name="pathselector" size="0" onFocus="select_path(this.form)" class="select-fix1">
            </select><br/>
        <input type="radio" name="pathinput" value="manual">
            ${_("Manual input")}
            <input type="text" name="pathname"" size=15
                onFocus="edit_path(this.form)"
                class="input-fix1">

        <div id="path">
        ## classic form: ${c.path_options}
        </div>
    </td>
</tr>
</table>

<input type="submit" name="submit" value='${_("Check Permissions")}' class="input-button">

${h.end_form()}

<hr size='0'>

## classic form: ${c.access_map_msg}

<div id='acl_msg'></div>

