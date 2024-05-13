from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField, BooleanField, FieldList, FormField
from wtforms.validators import DataRequired, Length, ValidationError
from qcheckserv.servers.models import Server, ServerGroup


class ServerGroupCreationForm(FlaskForm):
    server_group_id = HiddenField('Id')
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Create')
