from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField, SelectField, HiddenField
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed

class Upload_Form(FlaskForm):
    file = FileField('Upload your audio file', validators=[FileAllowed(['mp3', 'wav'], 'Only MP3 and WAV formats are allowed.'), DataRequired()])
    transcription_choice = SelectField('Choose Transcription Service', choices=[
        ('whisper', 'Whisper'),
        ('whisperx', 'WhisperX'),
        ('cross_comparison_algo', 'Cross Comparison Algorithms (Selects all)'),
        ('cross_comparison_model_size', 'Cross Comparison Whisper Sizes (Selects all model sizes)'),
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
        ('large-v2', 'Large v2'),
        ('large-v3', 'Large v3'),
        ('turbo', 'Turbo')
    ]
    )

    submit = SubmitField('Start Transcription')