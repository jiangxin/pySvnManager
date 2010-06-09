# Set change log file for your documents
CHANGELOG=../pysvnmanager-doc.changelog

DOC_REV=$(shell head -1 $(CHANGELOG) | sed -e "s/^\S*\s\+(\(.*:\)\?\(\S\+\)).*/\2/")
DOC_DATESTRING=$(shell grep "^ -- .* <.*>  .\+$$" $(CHANGELOG) | head -1 | sed -e "s/^.\+>  \(.\+\)$$/\1/g" )
DOC_DATE=$(shell date -d "$(DOC_DATESTRING)" +"%Y-%m-%d %H:%M:%S")

all: build

build:
	(cd user-guide  && DOC_REV="$(DOC_REV)" DOC_DATE="$(DOC_DATE)" RUBYOPT=rubygems rake all)

# vim: noet ts=4 sw=4
