#!/usr/bin/env python

from setuptools import setup

setup(name='oblif',
      version='0.1.0',
      description='Bytecode transformations to produce data-oblivious code',
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
