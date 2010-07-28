# Set change log file for your documents
USER_CHANGELOG=../pysvnmanager-doc-user.changelog
DEVEL_CHANGELOG=../pysvnmanager-doc-devel.changelog

USER_DOC_REV=$(shell head -1 $(USER_CHANGELOG) | sed -e "s/^\S*\s\+(\(\S\+\)).*/\1/")
USER_DOC_DATESTRING=$(shell grep "^ -- .* <.*>  .\+$$" $(USER_CHANGELOG) | head -1 | sed -e "s/^.\+>  \(.\+\)$$/\1/g" )
USER_DOC_DATE=$(shell date -d "$(USER_DOC_DATESTRING)" +"%Y-%m-%d %H:%M:%S")

DEVEL_DOC_REV=$(shell head -1 $(DEVEL_CHANGELOG) | sed -e "s/^\S*\s\+(\(\S\+\)).*/\1/")
DEVEL_DOC_DATESTRING=$(shell grep "^ -- .* <.*>  .\+$$" $(DEVEL_CHANGELOG) | head -1 | sed -e "s/^.\+>  \(.\+\)$$/\1/g" )
DEVEL_DOC_DATE=$(shell date -d "$(DEVEL_DOC_DATESTRING)" +"%Y-%m-%d %H:%M:%S")

STAMP_FILE=doc-build-stamp

all: build

build: $(STAMP_FILE)
$(STAMP_FILE):
	(cd user-guide && DOC_REV="$(USER_DOC_REV)"  DOC_DATE="$(USER_DOC_DATE)"  RUBYOPT=rubygems rake html)
	(cd user-guide && DOC_REV="$(USER_DOC_REV)"  DOC_DATE="$(USER_DOC_DATE)"  RUBYOPT=rubygems rake pdf)
	(cd dev-guide  && DOC_REV="$(DEVEL_DOC_REV)" DOC_DATE="$(DEVEL_DOC_DATE)" RUBYOPT=rubygems rake html)
	(cd dev-guide  && DOC_REV="$(DEVEL_DOC_REV)" DOC_DATE="$(DEVEL_DOC_DATE)" RUBYOPT=rubygems rake pdf)
	touch $(STAMP_FILE)

clean:
	rm -f $(STAMP_FILE)

# vim: noet ts=4 sw=4
