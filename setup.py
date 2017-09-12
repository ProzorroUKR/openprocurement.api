from setuptools import setup, find_packages
import os

version = '2.4'

requires = [
    'setuptools',
    'openprocurement.api>=2.4',
    'openprocurement.tender.openua>=2.4'
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
        'aboveThresholdUA.defense = openprocurement.tender.openuadefense.includeme:includeme'
    ]
}

setup(name='openprocurement.tender.openuadefense',
      version=version,
      description="",
      long_description=open("README.txt").read() + "\n" +
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
      url='https://github.com/openprocurement/openprocurement.tender.openuadefense',
      license='Apache License 2.0',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['openprocurement', 'openprocurement.tender'],
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=test_requires,
      extras_require={'test': test_requires, 'docs': docs_requires},
      test_suite="openprocurement.tender.openuadefense.tests.main.suite",
      entry_points=entry_points
      )
