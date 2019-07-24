from flask_wtf import FlaskForm
from wtforms.validators import InputRequired
from wtforms import StringField, BooleanField, HiddenField, SelectField

class EventAdminForm(FlaskForm):
    event_location = StringField('Event Name', [InputRequired()])
    person_group = StringField('Person Group', [InputRequired()])

class GameAdminForm(FlaskForm):
    game_round = SelectField('Game Round', coerce = int)

class GameModeForm(FlaskForm):
    game_mode = SelectField('Game Mode', choices=[('pending', 'Attractor Mode'), ('active', 'Active - No Winner'), ('winner', 'Winner!')])

class FindUserForm(FlaskForm):
    user_name = StringField('Twitter Handle', [InputRequired()])

class ConfirmUserForm(FlaskForm):
    user_name = HiddenField()
    user_confirmed = BooleanField('Confirm Player', [InputRequired()])