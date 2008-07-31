# -*- coding: utf-8 -*-
<html>
  <head>
    ${self.head_tags()}
    ${self.ajax_script()}
  </head>
  <body ${self.body_params()}>

  <div id="popup_shadow" style="z-index:100;visibility:hidden;display:none;position:absolute;top:0px;width:100%;height:100%;background:#000000;opacity:0.0;filter:alpha(opacity=0);"></div>
  <div id="popup_notices" style="z-index:101;border:1px solid gray;position:absolute;top:0;left:250px;visibility:hidden;display:none;background:#eeee20;">
     ${_("Loading, please wait...")}
  </div>

	${self.nav_bar()}
	
    ${next.body()}
  </body>
</html>

<%def name="head_tags()">
    <title>Override Me!</title>
</%def>

<%def name="nav_bar()">
  <table>
      <tr>
          <td>${h.link_to(_("Check permissions"), h.url_for(controller="check", id=None))}</td>
          <td>${h.link_to(_("Role management"), h.url(controller="role", id=None))}</td>
          <td>${h.link_to(_("ACL management"), h.url(controller="authz", id=None))}</td>
          <td>${h.link_to(_("Logs"), h.url(controller="logs", id=None))}</td>
          <td>welcome ${session.get('user')}</td>
          <td>${h.link_to(_("Logout"), h.url(controller="logout", id=None))}</td>
      </tr>
  </table>
</%def>

<%def name="ajax_script()">
${h.javascript_include_tag(builtins=True)}

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
</script>
</%def>

<%def name="body_params()"></%def>
