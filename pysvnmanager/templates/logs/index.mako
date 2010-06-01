## -*- coding: utf-8 -*-
<%inherit file="/base.mako" />

<%def name="head_tags()">
    <title>${_("Administration logs")}</title>
</%def>

<SCRIPT LANGUAGE="JavaScript">
function paginate(num)
{
    showNoticesPopup();
    var params = {page:num};
    new Ajax.Updater(
    	{success:'logs',failure:'logs'}, 
    	'${h.url(controller="logs", action="paginate")}',
    	{asynchronous:true, evalScripts:true, method:'post', 
    		onComplete:
    			function(request)
    				{hideNoticesPopup();
    				new Effect.Highlight("logs",{duration:1});},
    		parameters:params});
}

function get_selected_radio(radio)
{
	for (var i = 0; i<radio.length; i++)
	{
		if (radio[i].checked)
		{
			return i;
		}
	}
}

function get_selected_radio_value(radio)
{
	i = get_selected_radio(radio)
	return radio[i].value
}

function compare(form)
{
	left = get_selected_radio_value(document.main_form.left)
	right = get_selected_radio_value(document.main_form.right)
	showNoticesPopup();
    var params = {left:left, right:right};
	new Ajax.Updater(
    	{success:'compare',failure:'compare'}, 
    	'${h.url(controller="logs", action="compare")}',
    	{asynchronous:true, evalScripts:true, method:'post', 
    		onComplete:
    			function(request)
    				{hideNoticesPopup();
    				new Effect.Highlight("compare",{duration:1});},
    		parameters:params});

}
</SCRIPT>

<h2>${_("Administration logs")}</h2>

<form name="main_form" onSubmit="compare(); return false;">
<div id="logs">
<%
  context.write(c.display);
%>
</div>
<input type="submit" name="submit" value='${_("Compare revisions")}'>

<div id="compare"></div>

</form>
