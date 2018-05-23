ckan.module('confirm-tweet', function ($, _) {
                var self;

                return {
                    initialize: function () {
                        self                      = this;
                        self.options.disable_edit = self.options.disable_edit === 'True';
                        self.sandbox.client.getTemplate('edit_tweet.html', self.options, self._onReceiveSnippet);
                    },

                    _onReceiveSnippet: function (html) {
                        var url    = '/dataset/' + self.options.pkgid + '/tweet';
                        self.modal = $(html);
                        var form   = self.modal.find('#edit-tweet-form');   
                        form.submit(function (e) {
                            e.preventDefault();
                            $.post(url,
                                   form.serialize(),
                                   function (results) {
                                       self.modal.modal('hide');
                                       if (results === undefined || results === null) {
                                           self.flash_error('Tweet not posted due to unknown error.');
                                       }
                                       else if (!results.success) {
                                           self.flash_error('Tweet not posted! Error message: "' + results.reason + '".<br>Your tweet: "' + results.tweet + '".');
                                       }
                                       else {
                                           self.flash_success('Tweet posted!<br>Your tweet: "' + results.tweet + '"')
                                       }
                                   },
                                   'json'
                            )
                        });
                        self.modal.find('.no-tweet').click(function(e){
                            var url_tweet    = '/dataset/disable-tweet-popup';
                            $.post(url_tweet,
                                {},
                                function (results) {
                                    self.modal.modal('hide');
                                },
                                'json'
                            )
                        })
                        self.modal.modal().appendTo(self.sandbox.body);
                    },

                    flash: function (message, category) {
                        $('.flash-messages').append('<div class="alert ' + category + '">' + message + '</div>');
                    },

                    flash_error: function (message) {
                        this.flash(message, 'alert-error')
                    },

                    flash_success: function (message) {
                        this.flash(message, 'alert-success')
                    }
                }
            }
);