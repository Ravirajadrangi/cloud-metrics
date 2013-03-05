"""FutureGrid: Cloud Metrics

This project is the basis for providing several metrics as part of the
usage analysis of multiple cloud environments.  At this time
Eucalyptus is supported.
"""

from setuptools import setup, find_packages
import sys, os

#execfile ('VERSION.py')
# hack as VERSION does not get included in packaged tar file for some reason
version = '3.1.1'

classifiers = """\
Intended Audience :: Developers
Intended Audience :: Education
Intended Audience :: Science/Research
Development Status :: 3 - Alpha
Intended Audience :: Developers
License :: OSI Approved :: Apache Software License
Programming Language :: Python
Topic :: Database
Topic :: Software Development :: Libraries :: Python Modules
Operating System :: POSIX :: Linux
Programming Language :: Python :: 2.7
Operating System :: MacOS :: MacOS X
Topic :: Scientific/Engineering
Topic :: System :: Clustering
Topic :: System :: Distributed Computing
"""

if sys.version_info < (2, 7):
    _setup = setup
    def setup(**kwargs):
        if kwargs.has_key("classifiers"):
            del kwargs["classifiers"]
        _setup(**kwargs)

doclines = __doc__.split("\n")

#DISTUTILS_DEBUG=1

setup(
    name='fgmetric',
    version=version,
    description=doclines[0],
    long_description = "\n".join(doclines[2:]),
    classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='FutureGrid Eucalyptys Log File Analysis',
    author='Gregor von Laszewski, Hyungro Lee, Fugang Wang',
    maintainer='Gregor von Laszewski, Hyungro Lee',
    maintainer_email="laszewski@gmail.com",
    author_email='laszewski@gmail.com',
    url='https://github.com/futuregrid/futuregrid-cloud-metrics',
    license='Apache 2.0',
    package_dir = {'': '.'},
    packages = find_packages(exclude=['ez_setup', 'examples', 'tests']),
    #include_package_data=True,
    #zip_safe=True,
    #install_requires=[
    #    # -*- Extra requirements: -*-
    #],
    
    entry_points={
        'console_scripts':
            [
             'fg-cleanup-db = fgmetric.FGEucaMetricsDB:command_clean_database',
             'fg-euca-gather-log-files = fgmetric.FGCollectFiles:main',
             'fg-parser = fgmetric.FGParser:main',
             'fg-logparser = fgmetric.FGLogParser:main',
             'fg-metric-converter = fgmetric.FGConverter:main',
             'fg-metric = fgmetric.FGAnalyzer:main',
             'fg-metric-beta = fgmetric.FGMetrics:main',
             'fgmetric = fgmetric.FGMetricsCli:main',
             'fg-metric-cli = fgmetric.FGMetricsCli:main'
             ]},
    
    # install_requires = [
    #     'sphinxcontrib-issuetracker',
    #     'sphinxcontrib-googlechart',
    #     'setuptools',
    #     'cmd2',
    #     'pip',
    #     'pygooglechart',
    #     'mysql-python',
    #     'pymongo'
    #     ],
    )

    # Removed console script
    # 'fg-log-gz-decompressor = futuregrid.eucalyptus.analyzer.FGLogGzDecompressor:main',


# http://docs.python.org/distutils/introduction.html#distutils-simple-example
# http://docs.python.org/distutils/setupscript.html#setup-script
# http://mxm-mad-science.blogspot.com/2008/02/python-eggs-simple-introduction.html
