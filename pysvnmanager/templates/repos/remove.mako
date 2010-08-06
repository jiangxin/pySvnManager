## -*- coding: utf-8 -*-
## vim: et ts=4 sw=4
<%inherit file="/base.mako" />

<%def name="head_tags()">
    <title>${_("Remove repository")}</title>
</%def>

<%def name="body_params()">    onload="init_repos_list()" </%def>

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

    repos_list = $('repos_list');
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
            new Ajax.Request(
                '${h.url(controller="repos", action='remove_submit')}',
                {
                 asynchronous:true, evalScripts:true, method:'post',
                 onFailure:
                    function(request)
                        {set_message_box(request.responseText, 'error');},
                 onSuccess:
                    function(request)
                        {set_message_box_json(request.responseText);init_repos_list();},
                 onComplete:
                    function(request)
                        {hideNoticesPopup();set_message_box_json(request.responseText);init_repos_list();},
                 parameters:Form.serialize(this)
                });
            return false;">
        
<span class="title">
  ${_("Repository name:")}
</span>
    <select id="repos_list" name="repos_list" size="1" class="select-repos">
    </select>
    <br>
    <input type="submit" name="submit" value="${_("Remove repository")}" class="input-button">

</form>
