SOURCEDIR=pySvnManager

all:
	@echo "clean - remove *.deb and other temporary files."
	@echo "dir   - extract source package."
	@echo "build - generate config files for current dists and run dpkg-buildpackage"

clean:
	-rm -f ../../pysvnmanager_*changes ../../pysvnmanager_*.deb 
	-rm -rf $(SOURCEDIR)/.pc
	(cd $(SOURCEDIR); git co master .; git clean -f -d; git st )

dir: clean
	(cd $(SOURCEDIR); [ -d debian ] || ln -s $$(dirname $$(dirname $$(pwd)))/debian debian; git status || true)
	sudo setfacl -Rb $(SOURCEDIR) ../debian

build:
	(cd $(SOURCEDIR); make -f debian/rules debian/control)
	(cd $(SOURCEDIR); dpkg-buildpackage -b -rfakeroot)

.PHONY: all clean dir build
# vim: noet
