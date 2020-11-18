
import os
from setuptools import setup

HERE = os.path.abspath(os.path.join(__file__, ".."))
README = os.path.join(HERE, "README.md")

def readme():
    with open(README) as f:
        return f.read()

setup(name='convergence',
      version='0.3.0',
      description=('A Python program to Perform Calculations Associated with '
                   'a Grid Convergence Study'),
      long_description=readme(),
      long_description_content_type='text/markdown',
      license = "GPLv3",
      author='Mathew Topper',
      author_email='dataonlygreater@gmail.com',
      url='https://github.com/Data-Only-Greater/convergence',
      packages=['convergence'],
      python_requires='>=2.7, !=3.10.*, <4',
      extras_require={
        'test': ["pytest", "pytest-cov", "pytest-mock"]},
      entry_points = {'console_scripts': 
                  ['grid-convergence = convergence.interface:cl_interface']},
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Scientific/Engineering"],
      )
