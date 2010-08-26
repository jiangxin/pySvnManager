## -*- coding: utf-8 -*-
## vim: et ts=4 sw=4
<%inherit file="/base.mako" />

<%def name="head_tags()">
    <title>${_("ACL management")}</title>
</%def>

<%def name="body_params()"> onload="init_repos_list()" </%def>

<SCRIPT LANGUAGE="JavaScript">

<%
msg = 'var all_users = { '

for user in c.all_avail_users:
    msg += '\n"%s": "%s",' % (user[0], user[1])
msg = msg.strip().rstrip(',')
msg +=' };\n'
context.write(msg)
%>

// Display repos list only.
function show_init_form()
{
    $('repos_list_box').style.visibility = 'visible';
    $('repos_list_box').style.position = 'relative';

    $('repos_input_box').style.visibility = 'hidden';
    $('repos_input_box').style.position = 'absolute';

    $('admins_box').style.visibility = 'hidden';
    $('admins_box').style.position = 'absolute';

    $('path_list_box').style.visibility = 'hidden';
    $('path_list_box').style.position = 'absolute';

    $('path_input_box').style.visibility = 'hidden';
    $('path_input_box').style.position = 'absolute';

    $('authz_box').style.visibility = 'hidden';
    $('authz_box').style.position = 'absolute';

    $('action_box').style.visibility = 'hidden';
    $('action_box').style.position = 'absolute';
}

// Display repos_list, admins_input, path_list.
function show_repos_form()
{
    show_init_form();

    $('admins_box').style.visibility = 'visible';
    $('admins_box').style.position = 'relative';

    $('path_list_box').style.visibility = 'visible';
    $('path_list_box').style.position = 'relative';

    $('action_box').style.visibility = 'visible';
    $('action_box').style.position = 'relative';

    disable_save_btn();
    disable_delete_btn();
}

//
function show_module_form()
{
    show_repos_form();

    $('authz_box').style.visibility = 'visible';
    $('authz_box').style.position = 'relative';

    disable_save_btn();
    enable_delete_btn();
}

//
function show_new_module_form()
{
    show_module_form();

    $('path_list_box').style.visibility = 'hidden';
    $('path_list_box').style.position = 'absolute';

    $('path_input_box').style.visibility = 'visible';
    $('path_input_box').style.position = 'relative';

    $('authz_box').style.visibility = 'visible';
    $('authz_box').style.position = 'relative';

    disable_save_btn();
    disable_delete_btn();
}

//
function show_new_repos_form()
{
    show_repos_form();

    $('repos_list_box').style.visibility = 'hidden';
    $('repos_list_box').style.position = 'absolute';

    $('repos_input_box').style.visibility = 'visible';
    $('repos_input_box').style.position = 'relative';

    $('path_list_box').style.visibility = 'hidden';
    $('path_list_box').style.position = 'absolute';

    $('path_input_box').style.visibility = 'visible';
    $('path_input_box').style.position = 'relative';

    $('authz_box').style.visibility = 'visible';
    $('authz_box').style.position = 'relative';

    disable_save_btn();
    disable_delete_btn();
}

function new_repos()
{
    show_new_repos_form();

    document.main_form.admins.value = '';
    document.main_form.repos_input.value = '';
    document.main_form.path_input.value = '';
    document.main_form.path_list.options.length = 0;
    document.main_form.authz_list.options.length = 0;

    refresh_user_list();
}

function new_module()
{
    show_new_module_form();

    document.main_form.path_input.value = '';
    document.main_form.path_list.options.length = 0;
    document.main_form.authz_list.options.length = 0;

    refresh_user_list();
}

function uf_name(name, title)
{
    if (name.charAt(0)=='@')
        name = '${_('Group:')}'+name.substring(1,name.length);
    else if (name.charAt(0)=='&')
        name = '${_('Alias:')}'+name.substring(1,name.length);
    else if (name =='*')
        name = '${_('All users(with anon)')}';
    else if (name =='$authenticated')
        name = '${_('Known users')}';
    else if (name =='$anonymous')
        name = '${_('Anonymous')}';
    else if (all_users[name])
        name = ( title && '${_('User:')}' || '' ) + all_users[name];
    else
        name = ( title && '${_('User:')}' || '' ) + name;
    return name;
}

function uf_rule(name,rights)
{
    name = uf_name(name, true);
    if (rights == 'r')
    {
        rights = '${_('Readonly')}';
    }
    else if (rights == 'rw')
    {
        rights = '${_('Full')}';
    }
    else if (rights == '')
    {
        rights = '${_('Denied')}';
    }
    return name+' >>> '+rights;
}

function init_repos_list()
{
    showNoticesPopup();
    new Ajax.Request(
        '${h.url(controller="authz", action="init_repos_list")}',
        {asynchronous:true, evalScripts:true, method:'post',
            onComplete:
                function(request)
                    {hideNoticesPopup();ajax_init_repos_list(request.responseText);}
        });
    showGlobalMessage();
}

function ajax_init_repos_list(code)
{
    var id = new Array();
    var name = new Array();
    var total = 0;
    var revision = '';

    repos_list = document.main_form.repos_list;
    repos_list.options.length = 0;

    try {
        eval(code);
        for (var i=0; i < total; i++)
        {
            repos_list.options[i] = new Option(name[i], id[i]);
        }
        document.main_form.revision.value = revision;
    }
    catch(exception) {
        alert(exception);
    }

    repos_changed();
}

function repos_changed()
{
    var name = document.main_form.repos_list.value;
    var params = {select:name};
    var revision = '';

    if (name=='...'||name=='')
    {
        show_init_form();
    }
    else
    {
        show_repos_form();

        showNoticesPopup();
        new Ajax.Request(
            '${h.url(controller="authz", action="repos_changed")}',
            {asynchronous:true, evalScripts:true, method:'post',
                onComplete:
                    function(request)
                        {hideNoticesPopup();ajax_repos_changed(request.responseText);},
                parameters:params
            });
    }
}

function ajax_repos_changed(code)
{
    var id = new Array();
    var name = new Array();
    var total = 0;
    var admin_users = '';

    admins = document.main_form.admins;
    path_list = document.main_form.path_list;
    path_list.options.length = 0;

    try {
        eval(code);
        admins.value = admin_users;
        for (var i=0; i < total; i++)
        {
            path_list.options[i] = new Option(name[i], id[i]);
        }
        document.main_form.revision.value = revision;
    }
    catch(exception) {
        alert(exception);
    }

    path_changed();
}

function path_changed()
{
    var repos = document.main_form.repos_list.value;
    var path  = document.main_form.path_list.value;
    var params = {reposname:repos, path:path};

    if (path=='...'||path=='')
    {
        show_repos_form();
    }
    else
    {
        show_module_form();

        showNoticesPopup();
        new Ajax.Request(
            '${h.url(controller="authz", action="path_changed")}',
            {asynchronous:true, evalScripts:true, method:'post',
                onComplete:
                    function(request)
                        {hideNoticesPopup();ajax_path_changed(request.responseText);},
                parameters:params
            });
    }
}

function ajax_path_changed(code)
{
    var user = new Array();
    var rights = new Array();
    var total = 0;
    var revision = '';

    authz_list = document.main_form.authz_list;
    user_list = document.main_form.user_list;

    authz_list.options.length = 0;

    try {
        eval(code);
        for (var i=0; i < total; i++)
        {
            authz_list.options[i] = new Option(uf_rule(user[i],rights[i]), user[i]+' = '+rights[i]);
        }
        document.main_form.revision.value = revision;
    }
    catch(exception) {
        alert(exception);
    }
    refresh_user_list();
}

function refresh_user_list()
{
    var all_users_id = new Array();
    reposname = document.main_form.repos_list.value;
    authz_list = document.main_form.authz_list;
    user_list = document.main_form.user_list;
    user_list.options.length = 0;
    ml = new Array();

    for(var id in all_users) all_users_id.push(id);
    all_users_id.sort();

    for (var i=0; i < authz_list.options.length; i++)
    {
        tmp = authz_list.options[i].value.split('=');
        tmp = tmp[0];
        if (tmp[tmp.length-1] == ' ')
        {
            tmp = tmp.substring(0,tmp.length-1);
        }

        ml[i] = tmp;
    }
    ml.sort();

    for (var i=0,j=0,k=0; i<all_users_id.length; i++)
    {
        while(all_users_id[i]>ml[j] && j<ml.length-1)
            j+=1;

        if (all_users_id[i] == ml[j])
            continue;

        name = uf_name(all_users_id[i], false)
        user_list.options[k] = new Option(name, all_users_id[i]);
        k+=1;
    }
}

function add_authz()
{
    authz_list = document.main_form.authz_list;
    user_list = document.main_form.user_list;
    user_rights = document.main_form.user_rights;

    for (var i=0; i<user_rights.length; i++)
    {
        if (user_rights[i].checked)
        {
            user_rights[i].checked = false;
            break;
        }
    }
    if (i>= user_rights.length)
    {
        alert('${_("No rights selected! Please check proper rights for selected users.")}');
        return false;
    }
    if (user_rights[i].value == 'r')
        rights = 'r'
    else if (user_rights[i].value == 'w' || user_rights[i].value == 'rw')
        rights = 'rw'
    else if (user_rights[i].value == 'n' || user_rights[i].value == '')
        rights = ''
    else
    {
        alert('${_("Unknown rights: ")}'+user_rights[i].value);
        return false;
    }

    addlist = new Array();
    rawinput = document.main_form.username.value;
    for (var i=0; i<user_list.options.length; i++)
    {
        if (user_list.options[i].selected)
        {
            addlist.push(user_list.options[i].value);
            if (user_list.options[i].value == rawinput)
                rawinput = '';
        }
    }
    if (rawinput)
    {
        addlist.push(rawinput);
        document.main_form.username.value = '';
    }

    for (var i=0; i<addlist.length; i++)
    {
        rule = addlist[i] + ' = ' + rights
        display = uf_rule(addlist[i], rights)
        authz_list.options[authz_list.options.length] =  new Option(display, rule);
    }

    enable_save_btn();
    disable_delete_btn();
    refresh_user_list();
}

function move_authz()
{
    authz_list = document.main_form.authz_list;

    for (var i=authz_list.options.length-1; i>=0; i--)
    {
        if (authz_list.options[i].selected)
        {
            authz_list.options[i] = null;
        }
    }

    enable_save_btn();
    disable_delete_btn();
    refresh_user_list();
}

function save_authz(form)
{
    if($('repos_list_box').style.visibility == 'visible')
    {
        mode1 = "edit";
        reposname = form.repos_list.value;
    }
    else
    {
        mode1 = "new";
        reposname = form.repos_input.value;
    }

    if($('path_list_box').style.visibility == 'visible')
    {
        mode2 = "edit";
        path = form.path_list.value;
    }
    else
    {
        mode2 = "new";
        path = form.path_input.value;
    }

    var admins = form.admins.value;
    var revision = document.main_form.revision.value;

    if (path == '...')
        path = '';
    rules = "";

    for (var i=0; i<form.authz_list.length; i++)
    {
        rules += form.authz_list.options[i].value + '\n';
    }


    if (reposname == '')
    {
        alert('${_("Please input repository name.")}');
        return false;
    }

    if (mode1 == 'new' && path == '' && admins == '')
    {
        alert('${_("Save failed.")}');
        return false;
    }

    if (mode2 == 'new' && path =='')
    {
        alert('${_("Please input module path.")}');
        return false;
    }

    var params = {reposname:reposname, admins:admins, path:path, rules:rules, mode1:mode1, mode2:mode2, revision:revision};
    showNoticesPopup();
    new Ajax.Request(
        '${h.url(controller="authz", action="save_authz")}',
        {asynchronous:true, evalScripts:true, method:'post',
            onComplete:
                function(request)
                    {hideNoticesPopup();save_authz_complete(request.responseText, reposname);},
            parameters:params
        });
}

function save_authz_complete(message, reposname)
{
    if (message)
    {
        message = '${_("Update ACL failed:")}' + message;
        error_msg(message);
    }
    else
    {
        message = '${_("Update ACL successfully.")}';
        info_msg(message);
        if (document.main_form.repos_list.value == reposname)
        {
            repos_changed();
        }
        else
        {
            init_repos_list();
        }
    }
}

function delete_authz(form)
{

    var reposname = document.main_form.repos_list.value;
    var path = document.main_form.path_list.value;
    var revision = document.main_form.revision.value;
    if (path == '...')
    {
        alert('${_("No path selected.")}');
        return false;
    }
    var message = "\n\n\n" +
        "_________________________________________________\n\n" +
        "${_('Are you sure to delete module:')} " + reposname+':'+path + " ?\n" +
        "_________________________________________________\n\n\n"   +
        "${_('Click Ok to proceed, or click cancel')}";

    if (!confirm(message)) return;

    var params = {reposname:reposname, path:path, revision:revision};

    showNoticesPopup();
    new Ajax.Request(
        '${h.url(controller="authz", action="delete_authz")}',
        {asynchronous:true, evalScripts:true, method:'post',
            onComplete:
                function(request)
                    {hideNoticesPopup();delete_authz_complete(request.responseText,reposname, path);},
            parameters:params
        });
}

function delete_authz_complete(message, reposname, path)
{
    if (message)
    {
        message = '${_("Can not delete module ")}' + reposname + ':' + path + ' : ' + message;
        error_msg(message);
    }
    else
    {
        message = '${_("Successfully delete module:")}' + reposname + ':' + path;
        info_msg(message);
        repos_changed();
    }
}

function enable_save_btn()
{
    document.main_form.save_btn.disabled = false;
}

function disable_save_btn()
{
    document.main_form.save_btn.disabled = true;
}

function enable_delete_btn()
{
    document.main_form.delete_btn.disabled = false;
}

function disable_delete_btn()
{
    document.main_form.delete_btn.disabled = true;
}
</SCRIPT>


<h2>${_("ACL management")}</h2>

<form name="main_form" method="post">
<input type="hidden" name="revision" value="${c.revision}">
<DIV style="position:relative;" class=gainlayout>

<DIV id="repos_list_box" class=gainlayout>
<span class="title">
  ${_("Repository:")}
</span>
    <select name="repos_list" size="1" onChange='repos_changed()' class="select-repos">
    </select>
% if c.is_super_user:
    <a href="#" onclick='new_repos()'><img
        src="${h.url("/img/edit.png")}" title="${_("New repository")}" alt="(+)"></a>${_("New repository")}
% endif
</DIV>

<DIV id="repos_input_box" class=gainlayout style="visibility:hidden;">
<span class="title">
  ${_("Repository Name:")}
</span>
<input type="text" name="repos_input" onChange="enable_save_btn()" class="input-repos">
</DIV>

<DIV id="admins_box" class=gainlayout style="visibility:hidden;">
<span class="title">
  ${_("Administrators:")}
</span>
<input type="text" name="admins" size="25" maxlength="255" onChange="enable_save_btn();disable_delete_btn()" class="input-fix2">
</DIV>

</DIV>

<hr size='1'>

<DIV style="position:relative;" class=gainlayout>

<!-- begin: path_list box -->
<DIV id="path_list_box" class=gainlayout style="visibility:hidden;">

<span class="title">
  ${_("Module:")}
</span>
    <select name="path_list" size="1" onChange='path_changed()' class="select-mod">
    </select>
    <a href="#" onclick='new_module()'><img
        src="${h.url("/img/edit.png")}" title="${_("New module")}" alt="(+)"> ${_("New module")}</a>
</DIV>
<!-- end: path_list box -->

<!-- begin: path_input box -->
<DIV id="path_input_box" class=gainlayout style="visibility:hidden;">
<span class="title">
  ${_("Module Path:")}
</span>
    <input type="text" name="path_input" onChange="enable_save_btn()" class="input-fix2">
</DIV>
<!-- end: path_input box -->

<table class="list" width="80%">
<tr>
<td>

<!-- begin: authz box -->
<DIV id='authz_box' style="position:relative;" class=gainlayout style="visibility:hidden;">
<table width='100%' class="hidden">
<tr>
  <th align='center'>
    ${_("ACL")}
  </th>
  <th class="hide" width="10%">
  </th>
  <th align='center'>
    ${_("Users")}
  </th>
</tr>
<tr>
  <td align='right'>
    <select name="authz_list" size="10" class="select-col1" multiple></select>
  </td>
  <td class='button'>
    <a href='#' onClick='add_authz()'><img src="${h.url("/img/left.png")}" title="${_("Add membership")}" alt="${_("Add membership")}"></a>
    <br>
    <a href='#' onClick='move_authz()'><img src="${h.url("/img/right.png")}" title="${_("Remove membership")}" alt="${_("Remove membership")}"></a>
    <br>
  </td>
  <td>
    <select name="user_list" size="10" class="select-col2" multiple></select><br>
    <img src="${h.url("/img/edit.png")}" title="${_("Manual input")}" alt="${_("Manual input")}">
    <input type="text" name="username" size="10" maxlength="50" class="input-fix2"><br>
    <input type="radio" name="user_rights" value="r">${_("ReadOnly")}
    <input type="radio" name="user_rights" value="w">${_("Full")}
    <input type="radio" name="user_rights" value="n">${_("Denied")}
  </td>
</tr>
</table>
</div>
<!-- end: authz box -->

<!-- begin: action box -->
<DIV id='action_box' class=gainlayout style="visibility:hidden;">
<table width='100%' class="hidden">
<tr>
  <td align='center'>
    <input type="hidden" name="reposname">
    <input type="button" name="save_btn"   value='${_("Save")}' onClick="save_authz(this.form)" class="input-button">
    <input type="button" name="delete_btn" value='${_("Delete")}' onClick="delete_authz(this.form)" class="input-button">
    <input type="button" name="cancel_btn" value='${_("Cancel")}' onClick="repos_changed()" class="input-button">
  </td>
</tr>
</table>
</DIV>
<!-- end: action box -->

</td>
</table>

</DIV>

</form>
