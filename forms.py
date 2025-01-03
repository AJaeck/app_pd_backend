from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField, SelectField, HiddenField
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed

class Upload_Form(FlaskForm):
    file = FileField('Upload your audio file', validators=[FileAllowed(['mp3', 'wav'], 'Only MP3 and WAV formats are allowed.'), DataRequired()])
    transcription_choice = SelectField('Choose Transcription Service', choices=[
        ('google', 'Google Speech Recognition'),
        ('whisper-online', 'Whisper'),
        ('whisper-offline', 'Whisper (Offline)'),
        ('cross_comparison_algo', 'Cross Comparison Algorithms (Selects all)'),
        ('cross_comparison_model_size', 'Cross Comparison Whisper Sizes (Selects all model sizes)'),
        #('sphinx', 'Sphinx (offline)')
    ],
        validators=[DataRequired()]
    )
    # New HiddenField to capture the selected model size
    model_size = SelectField('Select Whisper Model Size', choices=[
        ('tiny', 'Tiny'),
        ('base', 'Base'),
        ('small', 'Small'),
        ('medium', 'Medium'),
        ('large', 'Large (~10 GB VRAM)'),
        ('turbo', 'Turbo')
    ]
    )

    submit = SubmitField('Start Transcription')