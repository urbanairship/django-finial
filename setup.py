# (c) 2013 Urban Airship and Contributors

from setuptools import setup, find_packages

from finial import VERSION

setup(
    name='django-finial',
    version='.'.join(map(str, VERSION)),
    description='Template, Static, and URL Overrides per User.',
    long_description=open('README.md').read(),
    author='Gavin McQuillan',
    author_email='gavin@urbanairship.com',
    url='http://github.com/urbanairship/django-finial',
    license='BSD',
    packages=find_packages(),
    include_package_data=True,
    package_data = { '': ['README.md'] },
    install_requires=[
        'django',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
