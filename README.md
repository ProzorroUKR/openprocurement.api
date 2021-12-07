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


## Related services projects

#### Document service (openprocurement.documentservice)

https://github.com/ProzorroUKR/openprocurement.documentservice

#### Tasks (prozorro_tasks)

Integrations tasks service

https://github.com/ProzorroUKR/prozorro_tasks

#### Auction (prozorro-auction)

Auction service

https://github.com/ProzorroUKR/prozorro-auction

https://github.com/ProzorroUKR/prozorro-auction-frontend

#### Auctions (openprocurement.auction)

Deprecated auction service

https://github.com/ProzorroUKR/openprocurement.auction

https://github.com/ProzorroUKR/openprocurement.auction.esco

https://github.com/ProzorroUKR/openprocurement.auction.js

https://github.com/ProzorroUKR/openprocurement.auction.esco-js

https://github.com/ProzorroUKR/openprocurement.auction.worker

#### Chronograph (prozorro_chronograph)

Chronograph service

#### Chronograph (openprocurement.chronograph)

Deprecated chronograph service

https://github.com/ProzorroUKR/openprocurement.chronograph

#### Bridges

API data bridges (contracting, competitive dialogue, framework agreement, price quotation)
