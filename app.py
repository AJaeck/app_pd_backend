from flask import Flask, request, jsonify, render_template, flash
from flask_bootstrap import Bootstrap5
from flask_wtf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
import uuid
from datetime import datetime
import os
import speech_recognition as sr
import ffmpeg
import secrets
from werkzeug.utils import secure_filename

#Import WTForms https://flask-wtf.readthedocs.io/en/1.0.x/
from forms import Upload_Form

app = Flask(__name__)
foo = secrets.token_urlsafe(16)
app.secret_key = foo
app.config['UPLOAD_FOLDER'] = 'static/audio_uploads/'
app.config['MAX_CONTENT_LENGTH'] = 250 * 1024 * 1024 # 25MB
app.config['UPLOAD_EXTENSIONS'] = ['.mp3', '.wav']

# Bootstrap-Flask requires this line
bootstrap = Bootstrap5(app)
# Flask-WTF requires this line
csrf = CSRFProtect(app)

# Allow CORS for development env
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

# Set the PATH environment variable
os.environ['PATH'] += os.pathsep + r"C:\Users\ajaec\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-7.0-full_build\bin"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()))
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    # No need to manually define the 'results' relationship here.

class Results(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    taps = db.Column(db.Integer, nullable=False)
    audio_file_path = db.Column(db.String(256), nullable=True)  # Path to the audio file
    transcription = db.Column(db.Text, nullable=True)  # Transcribed text

    user = db.relationship('User', backref=db.backref('results', lazy=True))

@app.route('/')
def hello_world():
    return render_template("index.html")

@app.route('/speech-analysis', methods=['GET', 'POST'])
def speech_analysis():
    form = Upload_Form()
    transcription_upload_audio = "test"

    if form.validate_on_submit():
        audio = form.file.data
        audio_filename = secure_filename(audio.filename)
        if audio_filename != '':
            file_ext = os.path.splitext(audio_filename)[1]
            if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                print(f'File Extension {file_ext} not supported')

            # Audio save to static audio folder
            audio_name = str(uuid.uuid1()) + "_" + audio_filename
            audio_path = os.path.join(app.config['UPLOAD_FOLDER'], audio_name)
            audio.save(audio_path)

            print(f"{audio_name} successfully uploaded to {app.config['UPLOAD_FOLDER']}")

            def transcribe_audio(file_path):
                # Initialize the recognizer
                r = sr.Recognizer()

                # Open the file
                with sr.AudioFile(file_path) as source:
                    # Adjust for ambient noise and record the audio
                    r.adjust_for_ambient_noise(source)
                    audio_data = r.record(source)

                    try:
                        # Recognize (convert from speech to text) using the default API key
                        text = r.recognize_google(audio_data, language='de-DE')
                        print(True, text)
                        return True, text
                    except sr.UnknownValueError:
                        # API was unable to understand the audio
                        print("Google Speech Recognition could not understand audio")
                        return False, "Google Speech Recognition could not understand audio"
                    except sr.RequestError as e:
                        # Request failed
                        print(False, f"Could not request results from Google Speech Recognition service; {e}")
                        return False, f"Could not request results from Google Speech Recognition service; {e}"

            # Call transcription function here
            success, transcription_upload_audio = transcribe_audio(audio_path)
            print(transcription_upload_audio)

            if success:
                print(f"{audio_name} successfully transcribed")
            else:
                flash(transcription_upload_audio, 'error')  # Show error message as flash message

    return render_template("speech-analysis.html", form=form, extensions=app.config['UPLOAD_EXTENSIONS'], transcription=transcription_upload_audio)

@app.route('/create-user', methods=['POST'])
def create_user():
    data = request.json
    dob_date = datetime.strptime(data['dob'], '%Y-%m-%d').date()  # Convert string to date object

    # Check if the user with the given details already exists
    existing_user = User.query.filter_by(first_name=data['first_name'], last_name=data['last_name'],
                                         dob=dob_date).first()
    if existing_user:
        return jsonify({"message": "User with the same details already exists!"}), 409

    new_user = User(first_name=data['first_name'], last_name=data['last_name'], dob=dob_date)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User created successfully!", "user_id": new_user.id}), 201

@app.route('/get-users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{"id": user.id, "first_name": user.first_name, "last_name": user.last_name, "dob": user.dob.strftime('%d.%m.%Y')} for user in users]), 200

@app.route('/get-user-data/<user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if user:
        user_data = {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "dob": user.dob.strftime('%d.%m.%Y'),
            "results": [{"date": result.date.strftime('%Y-%m-%d'), "taps": result.taps, "transcription": result.transcription} for result in user.results]
        }
        return jsonify(user_data), 200
    else:
        return jsonify({"message": "User not found"}), 404

@app.route('/delete-user/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    # Delete associated results
    Results.query.filter_by(user_id=user_id).delete()

    # Delete the user
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User and associated data deleted successfully!"}), 200


@app.route('/save-tapping-result/<user_id>', methods=['POST'])
def save_tapping_result(user_id):
    data = request.json

    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    tapping_result = Results(user_id=user_id, date=datetime.now(), taps=data['taps'])
    db.session.add(tapping_result)
    db.session.commit()
    return jsonify({"message": "Tapping result saved successfully!"}), 201

@app.route('/get-tapping-results/<user_id>', methods=['GET'])
def get_tapping_results(user_id):
    results = Results.query.filter_by(user_id=user_id).all()
    return jsonify([{"date": result.date.strftime('%Y-%m-%d'), "taps": result.taps} for result in results]), 200

@app.route('/upload-audio/<user_id>', methods=['POST'])
def upload_audio(user_id):
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{user_id}-{timestamp}-audiofile"
        original_filepath = os.path.join('static/audio_files', filename)  # Define your path to save audio files
        file.save(original_filepath)

        # Convert the file to WAV using ffmpeg-python
        wav_filepath = original_filepath.rsplit('.', 1)[0] + '.wav'
        convert_to_wav(original_filepath, wav_filepath)

        # Call transcription function here
        success, transcription_or_error = transcribe_audio(wav_filepath)

        # Optionally, remove files after processing
        os.remove(original_filepath)
        if success:

            # Save results to database - uncomment when needed again
            #new_speech_result = Results(user_id=user_id, date=datetime.utcnow(), taps=0, audio_file_path=wav_filepath, transcription=transcription_or_error)

            try:
                #db.session.add(new_speech_result)
                #db.session.commit()
                return jsonify({'message': 'File uploaded and processed successfully', 'transcription': transcription_or_error}), 200
            except Exception as e:
                db.session.rollback()
                print(f"Database transaction failed: {str(e)}")
                return jsonify({'error': f"Database error: {str(e)}"}), 500
        else:
            return jsonify(
                {'error': 'Transcription failed', 'reason': transcription_or_error}), 422  # 422 Unprocessable Entity

def convert_to_wav(input_path, output_path):
    ffmpeg.input(input_path).output(output_path).run()

def transcribe_audio(file_path):
    # Initialize the recognizer
    r = sr.Recognizer()

    # Open the file
    with sr.AudioFile(file_path) as source:
        # Adjust for ambient noise and record the audio
        r.adjust_for_ambient_noise(source)
        audio_data = r.record(source)

        try:
            # Recognize (convert from speech to text) using the default API key
            text = r.recognize_google(audio_data, language='de-DE')
            return (True, text)
        except sr.UnknownValueError:
            # API was unable to understand the audio
            print("Google Speech Recognition could not understand audio")
            return (False, "Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            # Request failed
            return (False, f"Could not request results from Google Speech Recognition service; {e}")

def init_db():
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    init_db()  # Uncomment this if you want to initialize the db every time you run the app
    app.run(debug=True)
