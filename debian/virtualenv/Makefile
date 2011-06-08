#############################################################################
## How to use PYPI and PYPILIMIT ?
##
## sudo PYPI=http://pypi.bj.ossxp.com/ ALLOWHOSTS=*bj.ossxp.com make all
#############################################################################

PYPI?=

ifdef PYPI
  EASYINSTALL:=easy_install --index-url $(PYPI) --find-links $(PYPI)
  ifdef ALLOWHOSTS
    EASYINSTALL:=$(EASYINSTALL) --allow-hosts $(ALLOWHOSTS)
  endif
else
  EASYINSTALL:=PIP_CONFIG_FILE=pip.conf pip install
endif

help:
	@cat README

all: env no-site-packages pylons with-site-packages

require-mirror:
	@if [ -z "$(PYPI)" ] && [ ! -f pip.conf ]; then \
		cat README; \
		echo "Error: create a pip.conf from pip.conf.in, to use PYPI mirror."; \
		exit 1; \
	fi

env: require-mirror
	## Create virtual environment using virtualenv
	[ ! -f bin/activate ] && virtualenv --no-site-packages . || true
	
pylons: env no-site-packages
	@## Install pylons and others
	@#(. bin/activate ; $(EASYINSTALL) pylons\>=1.0 Tempita\>=0.2 WebTest\>=1.1 WebError\>=0.10.1 WebOb\>=0.9.6.1 Mako\>=0.2.4 nose\>=0.10.4 decorator\>=2.3.2 simplejson\>=2.0.8 FormEncode\>=1.2.1 PasteScript\>=1.7.3 PasteDeploy\>=1.3.3 Paste\>=1.7.2 Beaker\>=1.3dev WebHelpers\>=1.0 Routes\>=1.12.3 Pygments\>=1.3.1 MarkupSafe\>=0.9.2 docutils babel sqlalchemy simplejson)
	@#(. bin/activate ; $(EASYINSTALL) pylons==1.0 Tempita==0.4 WebTest==1.2.1 WebError==0.10.2 WebOb==0.9.8 Mako==0.3.4 nose==0.11.4 decorator==3.2.0 simplejson==2.1.1 FormEncode==1.2.2 PasteScript==1.7.3 PasteDeploy==1.3.3 Paste==1.7.4 Beaker==1.5.4 WebHelpers==1.0 Routes==1.12.3 Pygments==1.3.1 MarkupSafe==0.9.2 docutils babel sqlalchemy simplejson)
	(. bin/activate ; $(EASYINSTALL) pylons\>=1.0 docutils babel sqlalchemy simplejson)
	make with-site-packages

with-site-packages:
	-@find lib -name no-global-site-packages.txt | while read x; do \
		d=`dirname $$x`; f=`basename $$x`; echo mv $$x $$d/with-$${f#no-}; \
		mv $$x $$d/with-$${f#no-}; \
		done


no-site-packages:
	-@find lib -name with-global-site-packages.txt | while read x; do \
		d=`dirname $$x`; f=`basename $$x`; echo mv $$x $$d/no-$${f#with-}; \
		mv $$x $$d/no-$${f#with-}; \
		done
	-@ls -d lib/python* | while read x; do \
		[ -d $$x ] || continue; \
		[ ! -f $$x/no-global-site-packages.txt ] && \
		touch $$x/no-global-site-packages.txt && \
		echo "create file: $$x/no-global-site-packages.txt" || true; \
		done

.PHONY: all env pylons no-site-packages with-site-packages

# vim: noet ts=4 sw=4
