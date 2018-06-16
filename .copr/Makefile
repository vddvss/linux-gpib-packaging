svnurl := "https://svn.code.sf.net/p/linux-gpib/code/trunk"
svnrev := $(shell sed -En "s|^%global svnrev\s+(\S+)\s*$$|\1|p" $(spec))
distarchive := $(shell rpmspec -P $(spec) | sed -En "s|^Source0:\s+(\S+)\s*$$|\1|p")
exportfolder := $(basename $(distarchive))

srpm:
	dnf -y install svn
	svn export -r $(svnrev) $(svnurl) $(exportfolder)
	zip -r $(distarchive) $(exportfolder)
	rpmbuild -D "dist %{nil}" -D "_srcrpmdir $(outdir)" -D "_sourcedir $(CURDIR)" -bs $(spec)

