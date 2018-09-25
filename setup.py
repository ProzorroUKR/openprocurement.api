import os
from setuptools import setup, find_packages

version = '2.4.3'

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()

requires = [
    'barbecue',
    'chaussette',
    'cornice',
    'couchdb-schematics',
    'gevent',
    'iso8601',
    'jsonpatch',
    'libnacl',
    'pbkdf2',
    'pycrypto',
    'pyramid_exclog',
    'requests',
    'rfc6266',
    'setuptools',
    'tzlocal',
    'openprocurement.api>=2.4',
    'openprocurement.tender.core>=2.4.1',
    'openprocurement.agreement.core',
    'openprocurement.agreement.cfaua',
]
test_requires = requires + [
    'webtest',
    'python-coveralls',
]
docs_requires = requires + [
    'sphinxcontrib-httpdomain',
]

entry_points = {
    'openprocurement.tender.core.plugins': [
        'closeFrameworkAgreementSelectionUA = openprocurement.tender.cfaselectionua.includeme:includeme'
    ],
    # 'openprocurement.api.migrations': [
        # 'cfaselectionua_tenders = openprocurement.tender.cfaselectionua.migration:migrate_data'
    # ]
}

setup(name='openprocurement.tender.cfaselectionua',
      version=version,
      description='openprocurement.tender.cfaselectionua',
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
      url='https://github.com/openprocurement/openprocurement.tender.cfaselectionua',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['openprocurement', 'openprocurement.tender'],
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=test_requires,
      extras_require={'test': test_requires, 'docs': docs_requires},
      test_suite="openprocurement.tender.cfaselectionua.tests.main.suite",
      entry_points=entry_points)
