from setuptools import setup
setup(name='pylimitbook',
      description='Simulation of limit book',
      url="https://github.com/danielktaylor/PyLimitBook",
      version='20161102',
      author='Daniel K Taylor',
      license='MIT',
      packages=['pylimitbook'],
      scripts=['bin/bookViewer.py',
               'bin/create_graphing_data.py',
               'bin/limitbook-convert-csv.py',
               'bin/limitbook-parse.py',
               'bin/limitbook-tseries.py'])
