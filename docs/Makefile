# Makefile for Sphinx documentation

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
PAPER         =
BUILDDIR      = build

SPHINXINTL    = sphinx-intl
LANG          = uk

# User-friendly check for sphinx-build
ifeq ($(shell which $(SPHINXBUILD) >/dev/null 2>&1; echo $$?), 1)
$(error The '$(SPHINXBUILD)' command was not found. Make sure you have Sphinx installed, then set the SPHINXBUILD environment variable to point to the full path of the '$(SPHINXBUILD)' executable. Alternatively you can add the directory with the executable to your PATH. If you don't have Sphinx installed, grab it from http://sphinx-doc.org/)
endif

# User-friendly check for sphinx-intl
ifeq ($(shell which $(SPHINXINTL) >/dev/null 2>&1; echo $$?), 1)
$(error The '$(SPHINXINTL)' command was not found. Make sure you have Sphinx installed, then set the SPHINXBUILD environment variable to point to the full path of the '$(SPHINXINTL)' executable. Alternatively you can add the directory with the executable to your PATH. If you don't have Sphinx installed, grab it from http://sphinx-doc.org/)
endif

# Internal variables.
PAPEROPT_a4     = -D latex_paper_size=a4
PAPEROPT_letter = -D latex_paper_size=letter
ALLSPHINXOPTS   = -d $(BUILDDIR)/doctrees $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) source
# the i18n builder cannot share the environment and doctrees with the others
I18NSPHINXOPTS  = $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) source

.PHONY: help clean html changes linkcheck doctest gettext locale lang

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  clean            to clean build files"
	@echo "  html             to make standalone HTML files"
	@echo "  gettext          to make PO message catalogs"
	@echo "  changes          to make an overview of all changed/added/deprecated items"
	@echo "  linkcheck        to check all external links for integrity"
	@echo "  locale-update    to update specified language’s po files from pot, yo can set LANG, e.g. make locale-update LANG=uk"
	@echo "  locale-build     to build specified language’s mo files, yo can set LANG, e.g. make locale-build LANG=uk"

clean:
	rm -rf $(BUILDDIR)/*

html:
	$(SPHINXBUILD) -b html $(ALLSPHINXOPTS) $(BUILDDIR)/html

gettext:
	$(SPHINXBUILD) -b gettext $(I18NSPHINXOPTS) $(BUILDDIR)/locale

changes:
	$(SPHINXBUILD) -b changes $(ALLSPHINXOPTS) $(BUILDDIR)/changes

linkcheck:
	$(SPHINXBUILD) -b linkcheck $(ALLSPHINXOPTS) $(BUILDDIR)/linkcheck

locale-update:
	$(SPHINXINTL) update -p $(BUILDDIR)/locale -l $(LANG) -w 0

locale-build:
	$(SPHINXINTL) build -l $(LANG)
