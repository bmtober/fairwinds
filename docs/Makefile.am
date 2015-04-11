## Process this file with automake to produce Makefile.in

# Process all tutorial files with:
# for n in {a..d} {0..9};do make "tutorial-0$n.html";done
# for n in *.adoc;do make "${n%adoc}html";done

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
		fairwinds-overview.html \
		fairwinds-equations.html \
		*.png

