from setuptools import setup, find_packages
import os

version = '1.0.10dp'

requires = [
    'esculator',
    'setuptools',
    'openprocurement.api>=2.4.20dp',
    'openprocurement.tender.openeu>=2.4.6dp',
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
        'esco = openprocurement.tender.esco.includeme:includeme',
    ],
}

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()

setup(name='openprocurement.tender.esco',
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
      url='https://github.com/openprocurement/openprocurement.tender.esco',
      license='Apache License 2.0',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['openprocurement', 'openprocurement.tender'],
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      extras_require={'test': test_requires, 'docs': docs_requires},
      test_suite="openprocurement.tender.esco.tests.main.suite",
      entry_points=entry_points)
