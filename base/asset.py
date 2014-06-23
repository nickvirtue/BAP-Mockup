import os
import sys
# path to lib direcotory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../lib'))

from wtforms import Form, BooleanField, StringField, validators, TextAreaField

class Asset(object):
    def __init__(self, name=None, email_address=None, phone_number=None, description=None):
        print name
        print email_address
        print phone_number
        print description
        self.id = email_address
        self.name = name
        self.author = email_address
        self.category = phone_number
        self.description = description
        self.content = description
        self.text = description

class AssetDto(object):
    def __init__(self, name=None, email_address=None, phone_number=None, description=None):
        self.id = email_address
        self.name = name
        self.email_address = email_address
        self.phone_number = phone_number
        self.description = description


class AssetForm(Form):
    name            = StringField('Name', [validators.Length(min=4, max=50)])
    email_address   = StringField('Email address', [
        validators.Length(min=6, message='Little short for an email address?'),
        validators.Email(message='That''s not a valid email address.')
    ])
    phone_number   = StringField('Phone number', [
        validators.Length(min=9, message='Little short for an phone number?'),
    ])
    description            = TextAreaField('Description', [validators.Length(min=4, max=2048)])
