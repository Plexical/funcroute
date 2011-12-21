# -*- coding: utf-8 -*-
"""pavement.py -- pavement for Funcroute.

Copyright 2011 Plexical. See LICENCE for permissions.
"""
import os
import sys

from paver.easy import *
from paver.setuputils import setup

setup(
    name='funcroute',
    py_modules=('funcroute'),
    version='0.2dev',
    author='Jacob Oscarson',
    author_email='jacob@plexical.com',
    install_requires=open(os.path.join('deps',
                                       'run.txt')).readlines()
)

@task
def virtualenv():
    "Prepares a checked out directory for development"
    if not os.path.exists(os.path.join('bin', 'pip')):
        sys.path.insert(0, os.path.join('deps', 'virtualenv.zip'))
        import virtualenv
        virtualenv.create_environment('.')
    else:
        print('Virtualenv already set up')

@needs('virtualenv')
@task
def env():
    "Ensure virtualenv exists and is up to date"
    sh('./bin/pip install -r deps/run.txt --upgrade')
    sh('./bin/pip install -r deps/developer.txt --upgrade')

@task
def clean():
    "Remove everything created by the build process"
    path('bin').rmtree()
    path('lib').rmtree()
    path('include').rmtree()
