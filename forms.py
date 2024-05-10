from flask_wtf import FlaskForm
from wtforms import FileField,SubmitField
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed

class Upload_Form(FlaskForm):
    file = FileField('Lade deine Audiodatei hoch', render_kw={'onchange': 'handleFiles(this.files)'}, validators=[
        FileAllowed(['mp3', 'wav'],
                    'Es sind nur folgende Formate erlaubt: .mp3, .wav'),
        DataRequired('Du hast keine Audio Datei hochgeladen')
    ])
    submit = SubmitField('Upload 🚀')