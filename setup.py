from setuptools import setup, find_packages
import os

version = '1.0.1'

entry_points = {
    'openprocurement.api.plugins': [
        'planning = openprocurement.planning.api:includeme'
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
      install_requires=[
          'setuptools',
          'openprocurement.api',
      ],
      entry_points=entry_points,
      )
