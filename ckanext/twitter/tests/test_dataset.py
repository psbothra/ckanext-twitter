import ckan.plugins as p
import nose
from ckan.tests.pylons_controller import PylonsTestCase
from ckanext.twitter.lib import (parsers as twitter_parsers)
from ckanext.twitter.tests.helpers import Configurer, DataFactory

eq_ = nose.tools.eq_


class TestDatasetMetadata(PylonsTestCase):
    @classmethod
    def setup_class(cls):
        super(TestDatasetMetadata, cls).setup_class()
        cls.config = Configurer()
        p.load('datastore')
        p.load('twitter')
        cls.df = DataFactory()

    @classmethod
    def teardown_class(cls):
        cls.config.reset()
        cls.df.destroy()
        p.unload('datastore')
        p.unload('twitter')

    def test_gets_dataset_author(self):
        pkg_dict = self.df.public_records
        eq_(pkg_dict['author'], 'Test Author',
            'Author is actually: {0}'.format(
                    pkg_dict.get('author', 'no author set')))

    def test_gets_dataset_title(self):
        pkg_dict = self.df.public_records
        eq_(pkg_dict['title'], u'A test package',
            'Title is actually: {0}'.format(
                    pkg_dict.get('title', 'no title set')))

    def test_gets_dataset_number_of_records_if_has_records(self):
        pkg_dict = self.df.public_records
        n_records = twitter_parsers.get_number_records(self.df.context,
                                                       pkg_dict['id'])
        eq_(n_records, 5,
            'Calculated number of records: {0}\nActual number: 5'.format(
                    n_records))

    def test_gets_dataset_number_of_records_if_no_records(self):
        pkg_dict = self.df.public_no_records
        n_records = twitter_parsers.get_number_records(self.df.context,
                                                       pkg_dict['id'])
        eq_(n_records, 0,
            'Calculated number of records: {0}\nActual number: 0'.format(
                    n_records))

    def test_gets_is_private(self):
        pkg_dict = self.df.public_records
        if pkg_dict.get('private', None) is None:
            access = 'unknown'
        elif pkg_dict.get('private', None):
            access = 'private'
        else:
            access = 'public'
        eq_(pkg_dict['private'], False,
            'Package is actually: {0}'.format(access))
