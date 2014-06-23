import os

import webapp2

from webapp2_extras import auth, sessions
from jinja2.runtime import TemplateNotFound
import jinja2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True,
)


class BaseRequestHandler(webapp2.RequestHandler):
    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)

        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def jinja2(self):
        """Returns a Jinja2 renderer cached in the app registry"""
        return jinja2.get_jinja2(app=self.app)

    @webapp2.cached_property
    def session(self):
        """Returns a session using the default cookie key"""
        return self.session_store.get_session()

    @webapp2.cached_property
    def auth(self):
        return auth.get_auth()

    @webapp2.cached_property
    def current_user(self):
        """Returns currently logged in user"""
        user_dict = self.auth.get_user_by_session()
        return self.auth.store.user_model.get_by_id(user_dict['user_id'])

    @webapp2.cached_property
    def user_model(self):
        """Returns the implementation of the user model.

        It is consistent with config['webapp2_extras.auth']['user_model'], if set.
        """
        return self.auth.store.user_model

    def display_message(self, message):
        """Utility function to display a template with a simple message."""
        params = {
            'message': message
        }
        self.render('templates/message.html', params)


    @webapp2.cached_property
    def logged_in(self):
        """Returns true if a user is currently logged in, false otherwise"""
        return self.auth.get_user_by_session() is not None

    def render(self, template_name, template_vars={}):
        print('render: {t}'.format(t=template_name))
        # Preset values for the template
        values = {
            'url_for': self.uri_for,
            'logged_in': self.logged_in,
            'flashes': self.session.get_flashes()
        }
        print(values)
        # Add manually supplied template values
        values.update(template_vars)
        print(values)


        # read the template or 404.html
        try:
            self.response.write(self.get_template(template_name).render(values))
        except TemplateNotFound:
            print('Template not found: '+template_name)
            self.abort(404)
        print('finish render')

    def redirect(self, uri, permanent=False, abort=False, code=None, body=None, flash=None):
        print('redirect: {uri}'.format(uri=uri))
        if flash is not None:
            self.add_flash(flash)
        webapp2.RequestHandler.redirect(self, uri, permanent, abort, code, body)
        print('finish redirect')


    def get_template(self, template):
        return JINJA_ENVIRONMENT.get_template(template)

    def add_flash(self, flash):
        self.session.add_flash(flash)

    def get_flashes(self):
        return self.session.get_flashes()