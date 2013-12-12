'''
    setup.py
    --------
    Simple distutils script, which in general streetsign use is probably
    pointless, but nevertheless is kind of useful for ReadTheDocs to be able
    to install streetsign_server as a module in its virtualenv.
'''

from distutils.core import setup

setup(
    name = 'streetsign_server',
    packages = ['streetsign_server', 'streetsign_server.views',
                                     'streetsign_server.logic',
                                     'streetsign_server.post_types',
                                     'streetsign_server.external_source_types'],
    version = "0.6",
    description = 'A simple python/flask/web based digital signage system',
    long_description=open('README.md','r').read(),
    author = 'Daniel Fairhead',
    author_email = 'danthedeckie@gmail.com',
    url = 'https://bitbucket.org/dfairhead/streetsign-server',
    keywords = ['flask', 'signage', 'web'],
    classifiers = ['Development Status :: 4 - Beta',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
                   'Programming Language :: Python :: 2.7',
                  ],
    )
