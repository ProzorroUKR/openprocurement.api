# OpenProcurement Api

## Installation

```
docker-compose build
docker-compose up
```

## Documentation

OpenProcurement is initiative to develop software 
powering tenders database and reverse auction.

'openprocurement.api' is component responsible for 
exposing the tenders database to brokers and public.

Documentation about this API is accessible at
https://prozorro-api-docs.readthedocs.io/en/latest/

### Install

1. Install requirements

```
virtualenv -p python2.7 venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Add "couchdb" to be resolved to localhost in /etc/hosts

```
echo "127.0.0.1 couchdb" >> /etc/hosts
```

3. To run couchdb if you don't have one

```
docker-compose up -d couchdb
```

### Update

Running tests to update http files::

```
py.test docs/tests  # all
py.test docs/tests/test_belowthreshold.py -k test_docs_milestones  # specific
```

### Build

Run

```
sphinx-build -b html docs/source/ docs/build/html
```

or

```
cd docs
make html
```

### Translation

For translation into *uk* (2 letter ISO language code), you have to follow the scenario:

1. Pull all translatable strings out of documentation

```
cd docs
make gettext
```

2. Update translation with new/changed strings

```
cd docs
sphinx-intl update -p build/locale -l uk -w 0
```

3. Update updated/missing strings in `docs/source/locale/<lang>/LC_MESSAGES/*.po` with your-favorite-editor/poedit/transifex/pootle/etc. to have all translations complete/updated.

4. Compile the translation

```
cd docs
sphinx-intl build
```
