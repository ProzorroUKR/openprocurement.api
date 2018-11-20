from setuptools import setup, find_packages
import os

version = '2.4.5dp'

requires = [
    'setuptools',
    'openprocurement.api>=2.4.20dp',
    'openprocurement.tender.core>=2.4.6dp',
    'openprocurement.tender.belowthreshold>=2.4.5dp',
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
        'aboveThresholdUA = openprocurement.tender.openua.includeme:includeme'
    ]
}

setup(name='openprocurement.tender.openua',
      version=version,
      description="",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Programming Language :: Python",
      ],
      keywords='',
      author='Quintagroup, Ltd.',
      author_email='info@quintagroup.com',
      url='https://github.com/openprocurement/openprocurement.tender.openua',
      license='Apache License 2.0',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['openprocurement', 'openprocurement.tender'],
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=test_requires,
      extras_require={'test': test_requires, 'docs': docs_requires},
      test_suite="openprocurement.tender.openua.tests.main.suite",
      entry_points=entry_points
      )
