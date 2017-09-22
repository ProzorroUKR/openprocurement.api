from setuptools import setup, find_packages
import os

version = '2.4'

requires = [
    'setuptools',
]

test_requires = requires + [
    'webtest',
    'python-coveralls',
    'openprocurement.tender.belowthreshold',
]

docs_requires = requires + [
    'sphinxcontrib-httpdomain',
]

api_requires = requires + [
    'openprocurement.api>=2.4',
    'openprocurement.tender.core',
]

entry_points = {
    'openprocurement.api.plugins': [
        'contracting = openprocurement.contracting.api:includeme'
    ],
    'openprocurement.api.migrations': [
        'contracts = openprocurement.contracting.api.migration:migrate_data'
    ]
}

setup(name='openprocurement.contracting.api',
      version=version,
      description="",
      long_description=open("README.rst").read(),
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
      url='https://github.com/openprocurement/openprocurement.contracting.api',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['openprocurement', 'openprocurement.contracting'],
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=test_requires,
      extras_require={'api': api_requires, 'test': test_requires,
                      'docs': docs_requires},
      entry_points=entry_points,
      )
