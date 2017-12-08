import ckan.plugins as p
import nose
from ckan.common import session
from ckan.tests.pylons_controller import PylonsTestCase
from ckanext.twitter.lib.helpers import TwitterJSHelpers, twitter_pkg_suitable
from ckanext.twitter.tests.helpers import Configurer, DataFactory

eq_ = nose.tools.eq_


class TestGetConfigVariables(PylonsTestCase):
    @classmethod
    def setup_class(cls):
        super(TestGetConfigVariables, cls).setup_class()
        p.load('datastore')
        p.load('twitter')
        cls.config = Configurer()
        cls.df = DataFactory()
        cls.js_helpers = TwitterJSHelpers()

    def teardown(self):
        self.config.reset()

    @classmethod
    def teardown_class(cls):
        cls.config.reset()
        cls.df.destroy()
        p.unload('datastore')
        p.unload('twitter')

    def test_gets_context(self):
        assert isinstance(self.js_helpers.context, dict)

    def test_returns_false_if_not_in_session(self):
        session.clear()
        eq_(self.js_helpers.tweet_ready(self.df.public_no_records['id']),
            False)

    def test_returns_true_if_is_in_session(self):
        session.setdefault('twitter_is_suitable',
                           self.df.public_no_records['id'])
        session.save()
        eq_(self.js_helpers.tweet_ready(self.df.public_no_records['id']), True)

    def test_gets_tweet(self):
        self.config.remove(['ckanext.twitter.new'])
        eq_(self.js_helpers.get_tweet(self.df.public_no_records['id']),
            'New dataset: "A test package" by Author (1 resource).')

    def test_not_suitable_if_does_not_exist(self):
        is_suitable = twitter_pkg_suitable(self.df.context, 'not-a-real-id')
        eq_(is_suitable, False)

    def test_not_suitable_if_not_active(self):
        # exists
        self.df.reload_pkg_dicts()
        assert self.df.public_records is not None

        # not active
        self.df.deactivate_package(self.df.public_records['id'])
        assert self.df.public_records['state'] != 'active'

        # not draft
        assert self.df.public_records['state'] != 'draft'

        # is suitable
        is_suitable = twitter_pkg_suitable(self.df.context,
                                           self.df.public_records['id'])
        eq_(is_suitable, False)

        # undo the deactivation
        self.df.activate_package(self.df.public_records['id'])

    def test_not_suitable_if_no_resources(self):
        # exists
        self.df.reload_pkg_dicts()
        assert self.df.public_records is not None

        # active
        eq_(self.df.public_records['state'], 'active')

        # has no resources
        self.df.remove_public_resources()
        eq_(len(self.df.public_records.get('resources', [])), 0)

        # is suitable
        is_suitable = twitter_pkg_suitable(self.df.context,
                                           self.df.public_records['id'])
        eq_(is_suitable, False)

        # undo
        self.df.refresh()

    def test_not_suitable_if_no_active_resources(self):
        pkg_dict = self.df.deactivate_public_resources()
        # exists
        assert pkg_dict is not None

        # active
        eq_(pkg_dict['state'], 'active')

        # has resources
        assert len(pkg_dict['resources']) > 0

        # resources are not active
        active_resources = [r['state'] == 'active' for r in
                            pkg_dict['resources']]
        eq_(any(active_resources), False,
            '{0}/{1} resources still active'.format(sum(active_resources),
                                                    len(active_resources)))

        # is suitable
        is_suitable = twitter_pkg_suitable(self.df.context,
                                           None, pkg_dict)
        eq_(is_suitable, False)

    def test_not_suitable_if_private(self):
        # exists
        self.df.reload_pkg_dicts()
        assert self.df.private_records is not None

        # active
        eq_(self.df.private_records['state'], 'active')

        # has resources
        assert len(self.df.private_records['resources']) > 0

        # resources are active
        active_resources = [r['state'] == 'active' for r in
                            self.df.private_records['resources']]
        eq_(any(active_resources), True)

        # is private
        eq_(self.df.private_records.get('private', False), True)

        # is suitable
        is_suitable = twitter_pkg_suitable(self.df.context,
                                           self.df.private_records['id'])
        eq_(is_suitable, False)

    def test_otherwise_suitable(self):
        # exists
        self.df.reload_pkg_dicts()
        assert self.df.public_records is not None

        # active
        eq_(self.df.public_records['state'], 'active')

        # has resources
        assert len(self.df.public_records['resources']) > 0

        # resources are active
        active_resources = [r['state'] == 'active' for r in
                            self.df.public_records['resources']]
        eq_(any(active_resources), True)

        # not private
        eq_(self.df.public_records.get('private', False), False)

        # is suitable
        is_suitable = twitter_pkg_suitable(self.df.context,
                                           self.df.public_records['id'])
        eq_(is_suitable, True)
