# Prozorro Openprocurement Api



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
virtualenv -p python3.8 venv
source venv/bin/activate
pip install -r docs/source/requirements.txt
```

2. Add "mongo" to be resolved to localhost in /etc/hosts

```
echo "127.0.0.1 mongo" >> /etc/hosts
```

3. To run mongo if you don't have one

```
docker-compose up -d mongo
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

3. Update updated/missing strings in `docs/locale/uk/LC_MESSAGES/*.po` with your-favorite-editor/poedit/transifex/pootle/etc to have all translations complete/updated.

4. Compile the translation

```
cd docs
sphinx-intl build
```


## Related services projects

### Current services projects

#### openprocurement.documentservice

Document service

https://github.com/ProzorroUKR/openprocurement.documentservice

#### prozorro_tasks

Integration tasks service

https://github.com/ProzorroUKR/prozorro_tasks

#### prozorro-auction

Auction service

https://github.com/ProzorroUKR/prozorro-auction

https://github.com/ProzorroUKR/prozorro-auction-frontend

#### prozorro_chronograph

Chronograph service

https://github.com/ProzorroUKR/prozorro_chronograph

#### prozorro-bridge-contracting

Contracting bridge

https://github.com/ProzorroUKR/prozorro-bridge-contracting

#### prozorro-bridge-frameworkagreement

Frameworkagreement bridge

https://github.com/ProzorroUKR/prozorro-bridge-frameworkagreement

#### prozorro-bridge-competitivedialogue

Competitivedialogue bridge

https://github.com/ProzorroUKR/prozorro-bridge-competitivedialogue

#### prozorro-bridge-pricequotation

Price Quotation bridge

https://github.com/ProzorroUKR/prozorro-bridge-pricequotation
