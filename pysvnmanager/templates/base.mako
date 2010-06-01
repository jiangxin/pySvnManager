# -*- coding: utf-8 -*-
<html>
  <head>
    ${self.head_tags()}
    ${self.ajax_script()}
    ${h.stylesheet_link(h.url('/css/common.css'), media='all')}

    <SCRIPT LANGUAGE="JavaScript">
<%
msg = ''
if hasattr(c, "global_message"):
    msg += "var global_message = \"%s\";\n" % c.global_message
else:
    msg += "var global_message = \"\";\n"
context.write(msg)
%>
    function showGlobalMessage()
    {
      if (global_message) {
          info_msg(global_message);
      }
    }
    </SCRIPT>
  </head>
  <body ${self.body_params()}>

  <div id="popup_shadow" style="z-index:100;visibility:hidden;display:none;position:absolute;top:0px;width:100%;height:100%;background:#000000;opacity:0.0;filter:alpha(opacity=0);"></div>
  <div id="popup_notices" style="z-index:101;border:1px solid gray;position:absolute;top:0;left:250px;visibility:hidden;display:none;background:#eeee20;">
     ${_("Loading, please wait...")}
  </div>

	${self.nav_bar()}

  <div id="message_box" style="visibility:hidden;position:absolute; margin:1em;" class=gainlayout>
  <div id="message"></div>
  &nbsp;&nbsp;&nbsp;&nbsp;<a class="clear-link" href="#" onClick="document.getElementById('message').innerHTML='';switch_message_box()">${_("Clear message")}</a>
  </div>
	
    ${next.body()}
  </body>
</html>

<%def name="head_tags()">
    <title>Override Me!</title>
</%def>

<%def name="nav_bar()">
  <table>
      <tr>
          <td>${h.link_to(_("Check permissions"), h.url(controller="check",action="index"))}</td>
          <td>${h.link_to(_("Role management"), h.url(controller="role",action="index"))}</td>
          <td>${h.link_to(_("ACL management"), h.url(controller="authz",action="index"))}</td>
          <td>${h.link_to(_("Repos management"), h.url(controller="repos",action="index"))}</td>
          <td>${h.link_to(_("Change log"), h.url(controller="logs",action="index"))}</td>
          <td>${_("Welcome")} ${session.get('user')}</td>
          <td>${h.link_to(_("Logout"), h.url("logout"))}</td>
      </tr>
  </table>
</%def>

<%def name="ajax_script()">
${h.javascript_link(h.url('/javascripts/prototype.js'))}
${h.javascript_link(h.url('/javascripts/scriptaculous.js'))}
${h.javascript_link(h.url('/javascripts/unittest.js'))}

<!-- IE layout bugfix -->
<!--[if lt IE 7]><style>
.gainlayout { height: 0; }
</style><![endif]-->

<!--[if IE 7]><style>
.gainlayout { zoom: 1;}
</style><![endif]-->

<script language='javascript'>
function getWinWidth()
{
    var winW = 630;

    if (parseInt(navigator.appVersion)>3) {
        if (navigator.appName=="Netscape") {
            winW = window.innerWidth;
        }
        if (navigator.appName.indexOf("Microsoft")!=-1) {
            winW = document.body.offsetWidth;
        }
    }
    return winW;
}
function getWinHeight()
{
    var winH = 460;

    if (parseInt(navigator.appVersion)>3) {
        if (navigator.appName=="Netscape") {
            winH = window.innerHeight;
        }
        if (navigator.appName.indexOf("Microsoft")!=-1) {
            winH = document.body.offsetHeight;
        }
    }
    return winH;
}
</script>

<script language='javascript'>
function showPopupShadow()
{
  document.getElementById('popup_shadow').style.visibility = 'visible';
  document.getElementById('popup_shadow').style.display = 'inline';
}

function hidePopupShadow()
{
  document.getElementById('popup_shadow').style.visibility = 'hidden';
  document.getElementById('popup_shadow').style.display = 'none';
}

function showNoticesPopup()
{
  showPopupShadow();

  document.getElementById('popup_notices').style.top= '0px';
  document.getElementById('popup_notices').style.left= getWinWidth()/2+'px';
  document.getElementById('popup_notices').style.visibility = 'visible';
  document.getElementById('popup_notices').style.display = 'inline';
}

function hideNoticesPopup()
{
  hidePopupShadow();

  document.getElementById('popup_notices').style.visibility = 'hidden';
  document.getElementById('popup_notices').style.display = 'none';
}

function warn_msg(message)
{
	set_message_box("<div class='warning'>"+message+"<div>");
}

function error_msg(message)
{
	set_message_box("<div class='error'>"+message+"<div>");
}

function info_msg(message)
{
	set_message_box("<div class='info'>"+message+"<div>");
}

function set_message_box(message)
{
	document.getElementById('message').innerHTML=message;
	switch_message_box();
}

function switch_message_box()
{
	c=document.getElementById('message').innerHTML;
	s=document.getElementById('message_box').style;
	if (c)
	{
		s.visibility='visible';
		s.position = 'relative';
	}
	else
	{
		s.visibility='hidden';
		s.position = 'absolute';
	}
}
</script>
</%def>

<%def name="body_params()"> onload="showGlobalMessage()" </%def>
