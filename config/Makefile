
SRCDIR=../pysvnmanager/config
CONFFILE=localconfig.py svn.access svn.passwd svn.access.test svn.passwd.test

all: $(CONFFILE) ../svnroot.test
	
clean:
	@-rm $(CONFFILE) >/dev/null 2>&1
	@-rm localconfig.pyc >/dev/null 2>&1
	@-rm -f *,v RCS/*test,v 2>&1
	@-rm -rf ../svnroot.test

%: $(SRCDIR)/%.in
	cp $< $@

%.test: $(SRCDIR)/%.example
	cp $< $@

../svnroot.test: ../pysvnmanager/tests/data/svnroot.tar.bz2
	@if [ ! -d $@ ]; then \
		tar -C .. -jxvf $< ; \
	fi

.PHONY : all clean 
