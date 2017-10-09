
from setuptools import setup

# def readme():
    # with open('README.rst') as f:
        # return f.read()

setup(name='convergence',
      version='0.1',
      description=('A Python program to Perform Calculations Associated with '
                   'a Grid Convergence Study'),
      # long_description=readme(),
      license = "GPLv3",
      author='Mathew Topper',
      author_email='dataonlygreater@gmail.com',
      url='https://github.com/H0R5E/convergence',
      packages=['convergence'],
      python_requires='==2.7.*',
      entry_points = {'console_scripts': 
                           ['grid-convergence = convergence:main']},
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Programming Language :: Python :: 2.7",
        "Topic :: Scientific/Engineering"],
      )
       
