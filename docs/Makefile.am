## Process this file with automake to produce Makefile.in

SUBDIRS = techtalk tutorial .

SOURCES = $(wildcard *.adoc)

TARGETS = $(SOURCES:%.adoc=%.html)

docs-local: $(TARGETS)

$(TARGETS): $(SOURCES)

autodoc:
	postgresql_autodoc -t dot -u postgres -d fairwinds

%.html: %.adoc
	asciidoc $<

clean-local:
	-rm \
		fairwinds-ad.html \
		fairwinds-overview.html \
		fairwinds-equations.html \
		*.png

