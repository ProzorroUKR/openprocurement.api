from setuptools import setup, find_packages
import os

version = '0.1.0'

requires = [
    'setuptools',
    'openprocurement.api>=2.4',
    'zope.configuration'
]
test_requires = requires + [
    'webtest',
    'mock',
    'pytest',
    'nose', # TODO: remove from travis
    'pytest-cov'
]
docs_requires = requires + [
    'sphinxcontrib-httpdomain',
]

entry_points = {
    'openprocurement.api.plugins': [
        'agreementCore = openprocurement.agreement.core.includeme:includeme'
    ],
}

setup(name='openprocurement.agreement.core',
      version=version,
      description="",
      long_description=open("README.md").read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Programming Language :: Python",
      ],
      keywords='',
      author='Quintagroup, Ltd.',
      author_email='info@quintagroup.com',
      # url='https://github.com/openprocurement/openprocurement.agreement.core',
      license='Apache License 2.0',
      packages=find_packages(exclude=['ez_setup']),
      package_data={'': ['*.zcml', '*.csv']},
      namespace_packages=['openprocurement', 'openprocurement.agreement'],
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=test_requires,
      extras_require={'test': test_requires, 'docs': docs_requires},
      # test_suite="openprocurement.agreement.core.tests.main.suite",
      entry_points=entry_points
      )
