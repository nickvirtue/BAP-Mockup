import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))

import base.sunburnt as sunburnt
# import base.solr_py as sunburnt
import wtforms

import datetime

import webapp2
import authentication

from webapp2_extras.auth import InvalidAuthIdError
from webapp2_extras.auth import InvalidPasswordError

from base.asset import *
from base.query import *
from base_handler import BaseRequestHandler
from secrets import SESSION_KEY


today = datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M%p")
solr_interface = sunburnt.SolrInterface("http://54.204.39.148:8983")
# solr_interface = sunburnt.Solr("http://54.204.39.148:8983/solr")


class DashboardHandler(BaseRequestHandler):

    @authentication.user_required
    def get(self):
        self.render('templates/dashboard.html', {})


class AssetsHandler(BaseRequestHandler):

    @authentication.user_required
    def get(self):
        self.render('templates/assets.html', {
            'form': AssetForm()
        })

    @authentication.user_required
    def post(self):
        form = AssetForm(self.request.POST)
        if form.validate():
            # solr_interface.update([Asset(name=form.name.data, email_address=form.email_address.data, phone_number=form.phone_number.data, description=form.description.data).__dict__])
            solr_interface.add(
                Asset(name=form.name.data, email_address=form.email_address.data, phone_number=form.phone_number.data,
                      description=form.description.data))
            solr_interface.commit()
            self.redirect(
                '/assets',
                flash='Asset added: {name}, {email}, {phone}'.format(name=form.name.data, email=form.email_address.data,
                                                                     phone=form.phone_number.data)
            )
        else:
            self.render('templates/assets.html', {
                'form': form
            })


class DeleteAssetsHandler(BaseRequestHandler):
    @authentication.user_required
    def get(self, asset_id):
        solr_interface.delete(asset_id)
        solr_interface.commit()
        self.render('templates/dashboard.html', {
            'form': QueryForm()
        })

class EditAssetsHandler(BaseRequestHandler):
    @authentication.user_required
    def get(self, asset_id):
        solr_interface.delete(asset_id)
        result = solr_interface.search('id:{id}'.format(id=asset_id))
        document = result['response']['docs'][0]

        assetDto = AssetDto(email_address=(document['author']), name=(document['name']),
                       phone_number=( document['category']), description=(document['description']))
        self.render('templates/assets.html', {
            'form': AssetForm(obj=assetDto)
        })


class QueryHandler(BaseRequestHandler):
    @authentication.user_required
    def get(self):
        self.render('templates/dashboard.html', {
            'form': QueryForm()
        })

    @authentication.user_required
    def post(self):
        form = QueryForm(self.request.POST)
        if form.validate():
            result = solr_interface.search(form.query.data)
            print '++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
            print result
            print '++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
            assets = []
            r = '<br />'
            for document in result['response']['docs']:
                id = document['id']

                try:
                    description = result['highlighting'][id]['description'][0]
                except:
                    description = document['description']
                assets.append(
                    AssetDto(
                        name=document['name'],
                        email_address=document['author'],
                        phone_number=document['category'],
                        description=description.replace('\r\n', r).replace('\n\r', r).replace('\r', r).replace('\n', r)))

            self.render('templates/dashboard.html', {
                'form': form,
                'assets': assets
            })
        else:
            self.render('templates/dashboard.html', {
                'form': form
            })


app = webapp2.WSGIApplication(
    [
        webapp2.Route('/', QueryHandler, name='home'),
        (r'/assets/delete/(.+)', DeleteAssetsHandler),
        (r'/assets/edit/(.+)', EditAssetsHandler),
        (r'/assets', AssetsHandler),
        (r'/query', QueryHandler),
        webapp2.Route('/<type:v|p>/<user_id:\d+>-<signup_token:.+>',
                      handler=authentication.VerificationHandler, name='verification'),
        webapp2.Route('/signup', authentication.SignupHandler, name='signup'),
        webapp2.Route('/login', authentication.LoginHandler, name='login'),
        webapp2.Route('/logout', authentication.LogoutHandler, name='logout'),
        webapp2.Route('/authenticated',authentication. AuthenticatedHandler, name='authenticated')
    ],
    debug=True,
    config={
        'webapp2_extras.sessions': {
            'cookie_name': '_simpleauth_sess',
            'secret_key': SESSION_KEY
        },
        'webapp2_extras.auth': {
            'user_model': 'user.User',
            'user_attributes': ['name']
        }
    }

)

