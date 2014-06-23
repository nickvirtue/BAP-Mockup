from wtforms import Form, StringField, validators


class QueryForm(Form):
    query            = StringField('Query', [validators.Length(min=1, max=1024)])
