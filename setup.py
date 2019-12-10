import os
from setuptools import setup, find_packages

version = '2.5.36.2'

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.md')) as f:
    README = f.read()

requires = [
    'barbecue',
    'chaussette',
    'cornice',
    'couchdb-schematics',
    'gevent',
    'iso8601',
    'isodate',
    'jsonpatch',
    'libnacl',
    'pbkdf2',
    'pycrypto',
    'pyramid_exclog',
    'requests',
    'rfc6266',
    'setuptools',
    'tzlocal',
    'zope.component',
    'zope.configuration',
    'esculator',
    'dateorro',
    'configparser',
]
test_requires = requires + [
    'webtest',
    'python-coveralls',
    'mock',
    'jmespath',
    'freezegun',
    'parameterized',
]
docs_requires = requires + [
    'sphinxcontrib-httpdomain',
]

entry_points = {
    'paste.app_factory': [
        'main = openprocurement.api.app:main'
    ],
    'openprocurement.api.plugins': [
        'api = openprocurement.api.includeme:includeme',
        'tender_core = openprocurement.tender.core.includeme:includeme',
        'planning = openprocurement.planning.api:includeme',
        'contracting = openprocurement.contracting.api:includeme',
        'agreementCore = openprocurement.agreement.core.includeme:includeme',
        'historical.core = openprocurement.historical.core.includeme:includeme',
        'historical.tender = openprocurement.historical.tender:includeme',
        'relocation = openprocurement.relocation.api:includeme'
    ],
    'openprocurement.tender.core.plugins': [
        'belowThreshold = openprocurement.tender.belowthreshold.includeme:includeme',
        'aboveThresholdUA = openprocurement.tender.openua.includeme:includeme',
        'aboveThresholdEU = openprocurement.tender.openeu.includeme:includeme',
        'aboveThresholdUA.defense = openprocurement.tender.openuadefense.includeme:includeme',
        'reporting = openprocurement.tender.limited.includeme:includeme',
        'negotiation = openprocurement.tender.limited.includeme:includeme_negotiation',
        'negotiation.quick = openprocurement.tender.limited.includeme:includeme_negotiation_quick',
        'competitivedialogue = openprocurement.tender.competitivedialogue.includeme:includeme',
        'esco = openprocurement.tender.esco.includeme:includeme',
        'closeFrameworkAgreementUA = openprocurement.tender.cfaua.includeme:includeme',
        'closeFrameworkAgreementSelectionUA = openprocurement.tender.cfaselectionua.includeme:includeme',
    ],
    'openprocurement.agreements.core.plugins': [
        'cfAgreementUA = openprocurement.agreement.cfaua.includeme:includeme'
    ],
    'openprocurement.api.migrations': [
        'tenders = openprocurement.api.migration:migrate_data',
        'contracts = openprocurement.contracting.api.migration:migrate_data',
        'plans = openprocurement.planning.api.migration:migrate_data',
    ],
    'console_scripts': [
        'bootstrap_api_security = openprocurement.api.database:bootstrap_api_security'
    ]
}

setup(name='openprocurement.api',
      version=version,
      description='openprocurement.api',
      long_description=README,
      classifiers=[
          "Framework :: Pylons",
          "License :: OSI Approved :: Apache Software License",
          "Programming Language :: Python",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Application"
      ],
      keywords="web services",
      author='Quintagroup, Ltd.',
      author_email='info@quintagroup.com',
      license='Apache License 2.0',
      url='https://github.com/openprocurement/openprocurement.api',
      package_dir={'': 'src'},
      py_modules=['cgi'],
      packages=find_packages('src'),
      namespace_packages=['openprocurement'],
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=test_requires,
      extras_require={'test': test_requires, 'docs': docs_requires},
      test_suite="openprocurement.api.tests.main.suite",
      entry_points=entry_points)
