import ckan.plugins as p
import nose
from ckan.tests.pylons_controller import PylonsTestCase
from ckanext.twitter.lib import (cache_helpers, parsers as twitter_parsers,
                                 twitter_api)
from ckanext.twitter.tests.helpers import Configurer, DataFactory

eq_ = nose.tools.eq_


class TestTweetGeneration(PylonsTestCase):
    @classmethod
    def setup_class(cls):
        super(TestTweetGeneration, cls).setup_class()
        cls.config = Configurer()
        p.load('datastore')
        p.load('twitter')
        cls.df = DataFactory()
        cache_helpers.reset_cache()

    def teardown(self):
        self.config.reset()

    @classmethod
    def teardown_class(cls):
        cls.config.reset()
        cls.df.destroy()
        p.unload('datastore')
        p.unload('twitter')

    def test_generates_tweet_if_public(self):
        tweet_text = twitter_parsers.generate_tweet(self.df.context,
                                                    self.df.public_records[
                                                        'id'],
                                                    is_new = True)
        assert tweet_text is not None

    def test_does_not_generate_tweet_if_private(self):
        tweet_text = twitter_parsers.generate_tweet(self.df.context,
                                                    self.df.private_records[
                                                        'id'],
                                                    is_new = True)
        eq_(tweet_text, None)

    def test_generates_correct_tweet_for_new(self):
        # delete the config value so it's using the default
        self.config.remove(['ckanext.twitter.new'])
        tweet_text = twitter_parsers.generate_tweet(self.df.context,
                                                    self.df.public_records[
                                                        'id'],
                                                    is_new = True)
        correct_tweet_text = 'New dataset: "A test package" by Author (' \
                             '5 records).'
        eq_(tweet_text, correct_tweet_text)

    def test_generates_correct_tweet_for_updated(self):
        # delete the config value so it's using the default
        self.config.remove(['ckanext.twitter.update'])
        tweet_text = twitter_parsers.generate_tweet(self.df.context,
                                                    self.df.public_records[
                                                        'id'],
                                                    is_new = False)
        correct_tweet_text = 'Updated dataset: "A test package" by Author' \
                             ' (5 records).'
        eq_(tweet_text, correct_tweet_text)

    def test_does_not_tweet_when_debug(self):
        self.config.update({
            'ckanext.twitter.debug': True
            })
        tweeted, reason = twitter_api.post_tweet('This is a test tweet.',
                                                 self.df.public_records['id'])
        eq_(tweeted, False)
        eq_(reason, 'debug')

    def test_shortens_author(self):
        # delete the config value so it's using the default
        self.config.remove(['ckanext.twitter.new'])
        self.df.destroy()
        self.df.long_author()
        self.df.create()
        pkg_dict = self.df.public_records
        tweet_text = twitter_parsers.generate_tweet(self.df.context,
                                                    pkg_dict['id'],
                                                    is_new = True)
        correct_tweet_text = 'New dataset: "A test package" by Dalton et al.' \
                             ' (5 records).'
        eq_(tweet_text, correct_tweet_text)
        self.df.refresh()

    def test_shortens_title(self):
        # delete the config value so it's using the default
        self.config.remove(['ckanext.twitter.new'])
        self.df.destroy()
        self.df.long_title()
        self.df.create()
        pkg_dict = self.df.public_records
        tweet_text = twitter_parsers.generate_tweet(self.df.context,
                                                    pkg_dict['id'],
                                                    is_new = True)
        correct_tweet_text = u'New dataset: "This is a very long package ' \
                             'title that\'s[...]" by Author (5 ' \
                             'records).'
        eq_(tweet_text, correct_tweet_text)
        self.df.refresh()

    def test_does_not_exceed_140_chars(self):
        # delete the config value so it's using the default
        self.config.remove(['ckanext.twitter.new'])
        self.df.destroy()
        self.df.long_author()
        self.df.long_title()
        self.df.create()
        pkg_dict = self.df.public_records
        force_truncate = twitter_parsers.generate_tweet(self.df.context,
                                                        pkg_dict['id'],
                                                        is_new = True)
        no_force = twitter_parsers.generate_tweet(self.df.context,
                                                  pkg_dict['id'],
                                                  is_new = True,
                                                  force_truncate = False)
        assert len(force_truncate) <= 140
        assert len(no_force) <= 140
        self.df.refresh()

    def test_does_not_tweet_when_recently_tweeted(self):
        # make sure it can't send an actual tweet by removing the credentials
        cache_helpers.reset_cache()
        self.config.remove(['ckanext.twitter.key', 'ckanext.twitter.secret',
                            'ckanext.twitter.token_key',
                            'ckanext.twitter.token_secret'])
        # turn off debug so it skips that check
        self.config.update({
            'debug': False,
            'ckanext.twitter.debug': False
            })
        # emulate successful tweet by manually inserting into the cache
        cache_helpers.cache(self.df.public_records['id'])
        # try to tweet
        tweeted, reason = twitter_api.post_tweet('This is a test tweet.',
                                                 self.df.public_records['id'])
        eq_(tweeted, False)
        eq_(reason, 'insufficient rest period')

    def test_does_tweet_when_new(self):
        # make sure it can't send an actual tweet by removing the credentials
        cache_helpers.reset_cache()
        self.config.remove(['ckanext.twitter.key', 'ckanext.twitter.secret',
                            'ckanext.twitter.token_key',
                            'ckanext.twitter.token_secret'])
        # turn off debug so it skips that check
        self.config.update({
            'debug': False,
            'ckanext.twitter.debug': False
            })
        # refresh the database to see if it's sending tweets during creation
        self.df.refresh()
        pkg_dict = self.df.public_records
        # try to tweet
        tweeted, reason = twitter_api.post_tweet('This is a test tweet.',
                                                 pkg_dict['id'])
        eq_(tweeted, False)
        eq_(reason, 'not authenticated')
