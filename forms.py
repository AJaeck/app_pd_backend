from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField, SelectField
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed

class Upload_Form(FlaskForm):
    file = FileField('Upload your audio file', validators=[FileAllowed(['mp3', 'wav'], 'Only MP3 and WAV formats are allowed.'), DataRequired()])
    transcription_choice = SelectField('Choose transcription service', choices=[
        ('google', 'Google Speech Recognition'),
        ('whisper', 'Whisper (OpenAI)'),
        #('google_cloud', 'Google Cloud Speech API'),
        #('wit', 'Wit.ai'),
        #('bing', 'Bing Speech'),
        #('houndify', 'Houndify'),
        #('ibm', 'IBM Speech to Text'),
        #('sphinx', 'Sphinx (offline)')
    ])
    submit = SubmitField('Start Transcription')

