#!/usr/bin/env python

try:
    from setuptools import setup, find_packages
except ImportError:
    import ez_setup
    ez_setup.use_setuptools()
    from setuptools import setup, find_packages
    
import os

data_files = []
for dir, dirs, files in os.walk('brookie'):
    for i, dirname in enumerate(dirs):
        if dirname.startswith('.'): del dirs[i]
    data_files.append((dir, [os.path.join(dir, file_) for file_ in files]))

setup(
    name = "django-brookie",
    version = "0.1",
    url = 'http://bitbucket.org/breadandpepper/django-brookie',
	download_url = 'http://bitbucket.org/breadandpepper/django-brookie/downloads/',
    license = 'BSD',
    description = "Brookie is a simple application for bookkeeping a small company within the django admin utility.",
    author = 'Petar Radosevic',
    author_email = 'petar@breadandpepper.com',
    packages = find_packages(),
    include_package_data = True,
    zip_safe = False,
    data_files = data_files,
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ]
)
