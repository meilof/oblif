#!/usr/bin/env python

from setuptools import setup

setup(name='oblif',
      version='0.3.1',
      description='Bytecode transformations to produce data-oblivious code',
      long_description = open("README.md").read(),
      long_description_content_type='text/markdown',
      author='Meilof Veeningen',
      author_email='meilof@gmail.com',
      url='https://github.com/meilof/oblif',
      packages=['oblif'],
      platforms=['any'],
      python_requires='>=3.8',
      license='MIT',
      classifiers=[
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License'
      ]
     )
