## -*- coding: utf-8 -*-
<%inherit file="/base.mako" />

<%def name="head_tags()">
    <title>${_("Repos management")}</title>
</%def>

<%def name="body_params()">	onload="init_repos_list()" </%def>

<SCRIPT LANGUAGE="JavaScript">

// Display repos list only.
function show_init_form()
{
	document.getElementById('repos_list_box').style.visibility = 'visible';
	document.getElementById('repos_list_box').style.position = 'relative';
	
	document.getElementById('new_hook_list_box').style.visibility = 'hidden';
	document.getElementById('new_hook_list_box').style.position = 'absolute';

	document.getElementById('new_hook_setting_box').style.visibility = 'hidden';
	document.getElementById('new_hook_setting_box').style.position = 'absolute';
			
	document.getElementById('remove_hook_box').style.visibility = 'visible';
	document.getElementById('remove_hook_box').style.position = 'relative';
}


function init_repos_list()
{
	showNoticesPopup();
	new Ajax.Request(
		'${h.url_for(controller="repos", action="init_repos_list")}', 
		{asynchronous:true, evalScripts:true, method:'post',
			onComplete:
				function(request)
					{hideNoticesPopup();ajax_init_repos_list(request.responseText);}
		});
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
		document.getElementById('remove_hook_form_content').innerHTML = "";
		show_init_form();
	}
	else
	{
		showNoticesPopup();
		new Ajax.Request(
			'${h.url_for(controller="repos", action="get_plugin_list")}', 
			{asynchronous:true, evalScripts:true, method:'post',
				onComplete:
					function(request)
						{hideNoticesPopup();ajax_repos_changed(request.responseText);},
				parameters:params
			});
			
		new Ajax.Updater(
			'remove_hook_form_content',
			'${h.url_for(controller="repos", action="get_remove_hook_form_content")}', 
			{asynchronous:true, evalScripts:true, method:'post',
				onComplete:
					function(request)
						{hideNoticesPopup();},
				parameters:params
			});
	}
}

function ajax_repos_changed(code)
{
	var id = new Array();
	var name = new Array();
	var total = 0;

	unset_plugin_list = document.main_form.unset_plugin_list;
	unset_plugin_list.options.length = 0;

	try {
		eval(code);
		if (total==1)
		{
			document.getElementById('new_hook_list_box').style.visibility = 'hidden';
			document.getElementById('new_hook_list_box').style.position = 'absolute';
			document.getElementById('new_hook_setting_box').style.visibility = 'hidden';
			document.getElementById('new_hook_setting_box').style.position = 'absolute';
		}
		else
		{
			document.getElementById('new_hook_list_box').style.visibility = 'visible';
			document.getElementById('new_hook_list_box').style.position = 'relative';
			for (var i=0; i < total; i++)
			{
				unset_plugin_list.options[i] = new Option(name[i], id[i]);
			}
		}
	}
	catch(exception) {
    	alert(exception);
	}
	
	path_changed();
}

function select_unset_hook_list()
{
	var reposname  = document.main_form.repos_list.value;
	var pluginname = document.main_form.unset_plugin_list.value;
	var params = {repos:reposname, plugin:pluginname};

	if (pluginname=='...'||pluginname=='')
	{
		document.getElementById('apply_new_hook_form_content').innerHTML = "";
		document.getElementById('new_hook_setting_box').style.visibility = 'hidden';
		document.getElementById('new_hook_setting_box').style.position = 'absolute';
	}
	else
	{
		document.getElementById('new_hook_setting_box').style.visibility = 'visible';
		document.getElementById('new_hook_setting_box').style.position = 'relative';
		showNoticesPopup();
		new Ajax.Updater(
			{success:'apply_new_hook_form_content',failure:'apply_new_hook_form_content'},
			'${h.url_for(controller="repos", action="get_hook_form")}', 
			{asynchronous:true, evalScripts:true, method:'post',
				onComplete:
					function(request)
						{hideNoticesPopup();},
				parameters:params
			});
	}
}

function apply_new_hook_form_submit(form)
{
	var reposname  = document.main_form.repos_list.value;
	var pluginname = document.main_form.unset_plugin_list.value;
	if (pluginname=='...'||pluginname==''||reposname=="..."||reposname=="")
	{
		alert("Bad repository or plugin name");
		return false;
	}
	form._repos.value = reposname;
	form._plugin.value = pluginname;
}

function remove_hook_form_submit(form)
{
	var reposname  = document.main_form.repos_list.value;
	if (reposname=="..."||reposname=="")
	{
		alert("Bad repository or plugin name");
		return false;
	}
	form._repos.value = reposname;
}

</SCRIPT>


<h2>${_("Repos management")}</h2>

<form name="main_form" method="post">
<input type="hidden" name="revision" value="${c.revision}">
<DIV style="position:relative;" class=gainlayout>

<DIV id="repos_list_box" class=gainlayout>
${_("Repository:")}
    <select name="repos_list" size="1" onChange='repos_changed()'>
    </select>
<a href="#" onclick='#'>[+${_("Add repository")}]</a>
<a href="#" onclick='#'>[-${_("Remove repository")}]</a>
</DIV>

<DIV id="new_hook_list_box" class=gainlayout style="visibility:hidden;position:absolute">
${_("Available hooks:")}
    <select name="unset_plugin_list" size="1" onChange='select_unset_hook_list()'>
    </select>
</form>
</DIV>
<DIV id="new_hook_setting_box" class=gainlayout style="visibility:hidden;position:absolute">
## <form name="apply_new_hook_form" method="post" action="${h.url_for(action='apply_new_hook')}"
##    	 onSubmit="apply_new_hook_form_submit(this)">
<%
    context.write( 
        h.form_remote_tag(
            html={'id':'apply_new_hook_form'}, 
            url=h.url(action='apply_new_hook'), 
            update=dict(success="message", failure="message"), 
            method='post', before='apply_new_hook_form_submit(this); showNoticesPopup()',
            complete='hideNoticesPopup();switch_message_box();repos_changed()',
        )
    )
 %>
    <input type=hidden name="_repos" value="">
    <input type=hidden name="_plugin" value="">
    <div id="apply_new_hook_form_content"></div>
    <input type="submit" name="apply" value="${_("Enable this hook")}">
</form>
</DIV>

<hr size='1'>

<DIV id="remove_hook_box" class=gainlayout style="visibility:visible;position:relative">
## <form name="remove_hook_form" method="post" action="${h.url_for(action='remove_hook')}"
##    	 onSubmit="remove_hook_form_submit(this)">
<%
    context.write( 
        h.form_remote_tag(
            html={'id':'remove_hook_form'}, 
            url=h.url(action='remove_hook'), 
            update=dict(success="message", failure="message"), 
            method='post', before='remove_hook_form_submit(this); showNoticesPopup()',
            complete='hideNoticesPopup();switch_message_box();repos_changed()',
        )
    )
 %>
    <input type=hidden name="_repos" value="">
    <div id="remove_hook_form_content"></div>
</DIV>

</DIV>

