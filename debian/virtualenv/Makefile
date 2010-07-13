help:
	@echo "make env:    create virtual env"
	@echo "make pylons: install pylons"
	@echo "make site-packages: virutal env use site-packages"

all: env pylons site-packages

env:
	## Create virtual environment using virtualenv
	[ ! -f bin/activate ] && virtualenv --no-site-packages . || true
	
pylons: env
	## Install pylons and others
	#(source  bin/activate ; easy_install pylons\>=1.0 Tempita\>=0.2 WebTest\>=1.1 WebError\>=0.10.1 WebOb\>=0.9.6.1 Mako\>=0.2.4 nose\>=0.10.4 decorator\>=2.3.2 simplejson\>=2.0.8 FormEncode\>=1.2.1 PasteScript\>=1.7.3 PasteDeploy\>=1.3.3 Paste\>=1.7.2 Beaker\>=1.3dev WebHelpers\>=1.0 Routes\>=1.12.3 Pygments\>=1.3.1 MarkupSafe\>=0.9.2 )
	#(source  bin/activate ; easy_install pylons==1.0 Tempita==0.4 WebTest==1.2.1 WebError==0.10.2 WebOb==0.9.8 Mako==0.3.4 nose==0.11.4 decorator==3.2.0 simplejson==2.1.1 FormEncode==1.2.2 PasteScript==1.7.3 PasteDeploy==1.3.3 Paste==1.7.4 Beaker==1.5.4 WebHelpers==1.0 Routes==1.12.3 Pygments==1.3.1 MarkupSafe==0.9.2 )
	(source  bin/activate ; easy_install pylons\>=1.0)

site-packages:
	find lib -name no-global-site-packages.txt | xargs rm -f

.PHONY: all env pylons site-packages

# vim: noet ts=4 sw=4
