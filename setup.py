from distutils.core import setup

setup(
    name = 'streetsign_server',
    packages = ['streetsign_server'],
    version = 0.5,
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
