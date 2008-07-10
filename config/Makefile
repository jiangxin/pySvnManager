
SRCDIR=../svnadmin/config
CONFFILE=localconfig.py svn.access svn.passwd

all: $(CONFFILE)
	
clean:
	@-rm $(CONFFILE) >/dev/null 2>&1
	@-rm localconfig.py >/dev/null 2>&1

%: $(SRCDIR)/%.in
	cp $< $@

.PHONY : all clean 
