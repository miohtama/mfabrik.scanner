from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='collective.eclipsescripts',
      version=version,
      description="Plone plug-in for Eclipse development",
      long_description=open("README.txt").read() + "\n",
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='mFabrik Research Oy',
      author_email='info@mfabrik.com',
      url='http://mfabrik.com',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      #namespace_packages=['gomobiletheme'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
