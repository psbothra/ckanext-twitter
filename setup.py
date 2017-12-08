from setuptools import setup, find_packages

version = '0.1'

setup(
    name='ckanext-twitter',
    version=version,
    description='Twitter DB updates',
    long_description='Sends a tweet every time a dataset is created or updated in the database.',
    classifiers=[],
    keywords='',
    author=['Alice Butcher'],
    author_email='data@nhm.ac.uk',
    url='https://github.com/NaturalHistoryMuseum/ckanext-twitter',
    license='',
    packages=find_packages(exclude=['ez_setup', 'list', 'tests']),
    namespace_packages=['ckanext', 'ckanext.twitter'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[],
    entry_points= \
        """
            [ckan.plugins]
            twitter=ckanext.twitter.plugin:TwitterPlugin
        """,
)
