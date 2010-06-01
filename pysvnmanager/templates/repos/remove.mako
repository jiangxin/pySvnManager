## -*- coding: utf-8 -*-
<%inherit file="/base.mako" />

<%def name="head_tags()">
    <title>${_("Remove repository")}</title>
</%def>

<%def name="body_params()">	onload="init_repos_list()" </%def>

<SCRIPT LANGUAGE="JavaScript">

function init_repos_list()
{
	showGlobalMessage();
	showNoticesPopup();
	var params = {filter:'blank'};
	new Ajax.Request(
		'${h.url(controller="repos", action="init_repos_list")}', 
		{asynchronous:true, evalScripts:true, method:'post',
			onComplete:
				function(request)
					{hideNoticesPopup();ajax_init_repos_list(request.responseText);},
			parameters:params
		});
}

function ajax_init_repos_list(code)
{
	var id = new Array();
	var name = new Array();
	var total = 0;
	
	repos_list = document.getElementById('repos_list');
	repos_list.options.length = 0;

	try {
		eval(code);
		for (var i=0; i < total; i++)
		{
			repos_list.options[i] = new Option(name[i], id[i]);
		}
	}
	catch(exception) {
    	alert(exception);
	}
}

</SCRIPT>

<h2>${_("Remove repository")}</h2>

##<form name="main_form" method="post" action="${h.url(controller="repos", action="remove_submit")}">

<form action="${h.url(controller="repos", action='remove_submit')}"
  id="main_form" method="POST"
  onsubmit="showNoticesPopup();
            new Ajax.Updater('message',
                             '${h.url(controller="repos", action='remove_submit')}',
                             {asynchronous:true, evalScripts:true, method:'post',
                              onComplete:function(request){hideNoticesPopup();switch_message_box();init_repos_list();},
                              parameters:Form.serialize(this)});
            return false;">

${_("Repository name:")}
    <select id="repos_list" name="repos_list" size="1">
    </select>
	<br>
    <input type="submit" name="submit" value="${_("Remove repository")}">

</form>
