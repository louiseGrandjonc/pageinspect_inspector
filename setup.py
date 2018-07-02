import os
from setuptools import setup, find_packages

version = __import__('inspector').__version__

root = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(root, 'README.rst')) as f:
    README = f.read()

setup(
    name='pageinspect-inspector',
    version=version,
    description='Draws the BTree for the pgindex of your choice',
    long_description=README,
    author='Louise Grandjonc',
    author_email='louise.grandjonc@gmail.com',
    # url='http://github.com/ulule/django-courriers',
    packages=['inspector'],
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        "psycopg2",
        "jinja2",
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities',
    ]
)
