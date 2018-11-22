from setuptools import setup, find_packages
import os

version = '2.4.6dp'

requires = [
    'setuptools',
    'openprocurement.api>=2.4.20dp',
]
test_requires = requires + [
    'webtest',
    'python-coveralls',
]
docs_requires = requires + [
    'sphinxcontrib-httpdomain',
]

entry_points = {
    'openprocurement.api.plugins': [
        'planning = openprocurement.planning.api:includeme'
    ],
    'openprocurement.api.migrations': [
        'plans = openprocurement.planning.api.migration:migrate_data'
    ]
}

setup(name='openprocurement.planning.api',
      version=version,
      description="",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='Quintagroup, Ltd.',
      author_email='info@quintagroup.com',
      license='Apache License 2.0',
      url='https://github.com/gorserg/openprocurement.planning.api',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['openprocurement', 'openprocurement.planning'],
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=test_requires,
      extras_require={'test': test_requires, 'docs': docs_requires},
      test_suite="openprocurement.planning.api.tests.main.suite",
      entry_points=entry_points,
      )
