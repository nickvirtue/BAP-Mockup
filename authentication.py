import os
import sys
# path to lib direcotory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../lib'))

from wtforms import Form, BooleanField, StringField, validators, TextAreaField

import logging
from webapp2_extras.auth import InvalidAuthIdError
from webapp2_extras.auth import InvalidPasswordError
from base_handler import BaseRequestHandler


class LoginForm(Form):
    username            = StringField('Username', [validators.Length(min=4, max=50)])
    password   = StringField('Password', [
        validators.Length(min=6, message='Little short for a password?')
    ])

class SignupForm(Form):
    user_name            = StringField('Username', [validators.Length(min=4, max=50)])
    password   = StringField('Password', [
        validators.Length(min=6, message='Little short for a password?')
    ])
    email   = StringField('Email address', [
        validators.Length(min=6, message='Little short for an email address?'),
        validators.Email(message='That''s not a valid email address.')
    ])
    name = StringField('Name', [validators.Length(min=4, max=50)])
    last_name = StringField('Last name', [validators.Length(min=4, max=50)])



def user_required(handler):
    """
      Decorator that checks if there's a user associated with the current session.
      Will also fail if there's no session present.
    """
    def check_login(self, *args, **kwargs):
        auth = self.auth
        if not auth.get_user_by_session():
            self.redirect(self.uri_for('login'), abort=True)
        else:
            return handler(self, *args, **kwargs)

    return check_login


class SignupHandler(BaseRequestHandler):
    def get(self):
        self._serve_page()

    def post(self):
        form = SignupForm(self.request.POST)
        if form.validate():

            user_name = form.user_name.data
            email = form.email.data
            name = form.name.data
            password = form.password.data
            last_name = form.last_name.data

            unique_properties = ['email_address']
            user_data = self.user_model.create_user(user_name,
                                                    unique_properties,
                                                    email_address=email, name=name, password_raw=password,
                                                    last_name=last_name, verified=False)
            if not user_data[0]: #user_data is a tuple
                self.display_message('Unable to create user for email %s because of \
            duplicate keys %s' % (user_name, user_data[1]))
                return

            print "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
            user = user_data[1]
            user_id = user.get_id()

            token = self.user_model.create_signup_token(user_id)

            verification_url = self.uri_for('verification', type='v', user_id=user_id,
                                            signup_token=token, _full=True)

            msg = 'Send an email to user in order to verify their address. \
              They will be able to do so by visiting  <a href="{url}">{url}</a>'

            self.display_message(msg.format(url=verification_url))
        else:
            self._serve_page(form)

    def _serve_page(self, form=SignupForm()):
        params = {
            'form': form
        }
        self.render('templates/signup.html', params)


class VerificationHandler(BaseRequestHandler):
    def get(self, *args, **kwargs):
        user = None
        user_id = kwargs['user_id']
        signup_token = kwargs['signup_token']
        verification_type = kwargs['type']

        # it should be something more concise like
        # self.auth.get_user_by_token(user_id, signup_token
        # unfortunately the auth interface does not (yet) allow to manipulate
        # signup tokens concisely
        user, ts = self.user_model.get_by_auth_token(int(user_id), signup_token,
                                                     'signup')

        if not user:
            logging.info('Could not find any user with id "%s" signup token "%s"',
                         user_id, signup_token)
            self.abort(404)

        # store user data in the session
        self.auth.set_session(self.auth.store.user_to_dict(user), remember=True)

        if verification_type == 'v':
            # remove signup token, we don't want users to come back with an old link
            self.user_model.delete_signup_token(user.get_id(), signup_token)

            if not user.verified:
                user.verified = True
                user.put()

            self.display_message('User email address has been verified.')
            return
        elif verification_type == 'p':
            # supply user to the page
            params = {
                'user': user,
                'token': signup_token
            }
            self.render('resetpassword.html', params)
        else:
            logging.info('verification type not supported')
            self.abort(404)


class LoginHandler(BaseRequestHandler):
    def get(self):
        self._serve_page()

    def post(self):
        form = LoginForm(self.request.POST)
        if form.validate():
            try:
                u = self.auth.get_user_by_password(form.username.data, form.password.data, remember=True,
                                                   save_session=True)
                self.redirect(self.uri_for('home'))
            except (InvalidAuthIdError, InvalidPasswordError) as e:
                logging.info('Login failed for user %s because of %s', form.username.data, type(e))
                self._serve_page(failed=True, form=form)
        else:
            self._serve_page(True, form)

    def _serve_page(self, failed=False, form=LoginForm()):
        params = {
            'failed': failed,
            'form': form
        }
        self.render('templates/login.html', params)


class LogoutHandler(BaseRequestHandler):
    def get(self):
        self.auth.unset_session()
        self.redirect(self.uri_for('home'))


class AuthenticatedHandler(BaseRequestHandler):
    @user_required
    def get(self):
        self.render('authenticated.html')
