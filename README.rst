Documentation
=============

OpenProcurement is initiative to develop software 
powering tenders database and reverse auction.

This documentation is available at http://api-docs.openprocurement.org/projects/limited/en/latest/index.html

Full documentation about OpenProcurement API is accessible at
http://api-docs.openprocurement.org/

Building documentation
----------------------

Use following commands to build documentation from `docs/source` into `docs/html`::

 python bootstrap.py -c docs.cfg
 bin/buildout -N -c docs.cfg
 bin/docs

For translation into *<lang>* (2 letter ISO language code), you have to follow the scenario:

 1. Pull all translatable strings out of documentation::

     (cd docs/_build; make gettext)

 2. Update translation with new/changed strings::

     bin/sphinx-intl update -c docs/source/conf.py -p docs/_build/locale -l <lang>
    
 3. Update updated/missing strings in `docs/source/locale/<lang>/LC_MESSAGES/*.po` with your-favorite-editor/poedit/transifex/pootle/etc. to have all translations complete/updated.

 4. Compile the translation::

      bin/sphinx-intl build -c docs/source/conf.py

 5. Build translated documentations::

     (cd docs/_build; make -e SPHINXOPTS="-D language='uk'" html)
