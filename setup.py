from setuptools import setup, find_packages
import os

version = '2.3.19'

requires = [
    'setuptools',
    'openprocurement.api>=2.3',
    'openprocurement.tender.openua',
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
        'reporting = openprocurement.tender.limited:includeme',
        'negotiation = openprocurement.tender.limited:includeme_negotiation',
        'negotiation.quick = openprocurement.tender.limited:includeme_negotiation_quick'
    ]
}

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()

setup(name='openprocurement.tender.limited',
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
      url='https://github.com/openprocurement/openprocurement.tender.limited',
      license='Apache License 2.0',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['openprocurement', 'openprocurement.tender'],
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      extras_require={'test': test_requires, 'docs': docs_requires},
      test_suite="openprocurement.tender.limited.tests.main.suite",
      entry_points=entry_points)
