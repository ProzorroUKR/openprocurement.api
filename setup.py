from setuptools import setup, find_packages

version = '0.0.1'

requires = [
    'setuptools',
]

test_requires = requires + [
    'webtest',
    'python-coveralls',
]

api_requires = requires + [
    'openprocurement.api',
]

entry_points = {
    'openprocurement.api.plugins': [
        'historical.core = openprocurement.historical.core:includeme'
    ],
}

setup(name='openprocurement.historical.core',
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
      url='https://github.com/openprocurement/openprocurement.historical.core',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['openprocurement', 'openprocurement.historical'],
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=test_requires,
      extras_require={
          'api': api_requires,
          'test': test_requires,
      },
      entry_points=entry_points
      )
