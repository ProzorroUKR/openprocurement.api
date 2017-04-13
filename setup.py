from setuptools import setup, find_packages
import os

version = '1.0.15'

requires = [
    'setuptools'
]

api_requires = requires + [
    'openprocurement.api>=2.3',
    'openprocurement.tender.openua',
    'openprocurement.tender.openeu'
]

test_requires = api_requires + requires + [
    'webtest',
    'python-coveralls',
]

docs_requires = requires + [
    'sphinxcontrib-httpdomain',
]

entry_points = {
    'console_scripts': [
        'competitive_dialogue_data_bridge = openprocurement.tender.competitivedialogue.databridge:main'
    ],
    'openprocurement.api.plugins': [
        'competitivedialogue = openprocurement.tender.competitivedialogue:includeme'
    ]
}

databridge_requires = requires + [
    'PyYAML',
    'gevent',
    'LazyDB',
    'ExtendedJournalHandler',
    'openprocurement_client>=1.0b2'
]

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.md')) as f:
    README = f.read()

setup(name='openprocurement.tender.competitivedialogue',
      version=version,
      description="",
      long_description=README,
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        ],
      keywords="web services",
      author='Quintagroup, Ltd.',
      author_email='info@quintagroup.com',
      url='https://github.com/openprocurement/openprocurement.tender.competitivedialogue',
      license='Apache License 2.0',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['openprocurement', 'openprocurement.tender'],
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      extras_require={'test': test_requires, 'docs': docs_requires,
                      'databridge': databridge_requires, 'api': api_requires},
      test_suite="openprocurement.tender.competitivedialogue.tests.main.suite",
      entry_points=entry_points)
