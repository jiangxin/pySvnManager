
SRCDIR=../pysvnmanager/config
CONFFILE=localconfig.py svn.access svn.passwd svn.access.test svn.passwd.test

all: $(CONFFILE)
	
clean:
	@-rm $(CONFFILE) >/dev/null 2>&1
	@-rm localconfig.pyc >/dev/null 2>&1
	@-rm -f *,v RCS/*test,v 2>&1

%: $(SRCDIR)/%.in
	cp $< $@

%.test: $(SRCDIR)/%.in
	cp $< $@


.PHONY : all clean 
