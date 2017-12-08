import json

import ckan.plugins
import nose
from ckan.lib.helpers import url_for
from ckan.new_tests import factories, helpers
from ckanext.twitter.tests.helpers import Configurer

eq_ = nose.tools.eq_


class TestController(object):
    @classmethod
    def setup_class(cls):
        cls.config = Configurer()
        cls.app = helpers._get_test_app()
        ckan.plugins.load('twitter')

    @classmethod
    def teardown_class(cls):
        cls.config.reset()
        ckan.plugins.unload('twitter')
        helpers.reset_db()

    def test_url_created(self):
        url = url_for('post_tweet', pkg_id = 'not-a-real-id')
        eq_(url, '/dataset/not-a-real-id/tweet')

    def test_url_ok(self):
        url = url_for('post_tweet', pkg_id = 'not-a-real-id')
        response = self.app.post(url)
        eq_(response.status_int, 200)

    def test_debug_post_tweet(self):
        dataset = factories.Dataset(
                notes = 'Test dataset'
                )
        url = url_for('post_tweet', pkg_id = dataset['id'])
        response = self.app.post(url, {
            'tweet_text': 'this is a test tweet'
            })
        body = json.loads(response.body)
        eq_(body['reason'], 'debug')
        eq_(body['tweet'], 'this is a test tweet')
        eq_(body['success'], False)
