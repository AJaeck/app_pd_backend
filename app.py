from flask import Flask, request, jsonify, render_template, flash
from flask_bootstrap import Bootstrap
from flask_wtf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
import uuid
from datetime import datetime
import os
import time
import secrets
from werkzeug.utils import secure_filename

#Import WTForms https://flask-wtf.readthedocs.io/en/1.0.x/
from forms import Upload_Form
# Importing the speech processing functions
from speechprocessing import SpeechTranscriber, convert_to_wav, feature_extraction

app = Flask(__name__)
foo = secrets.token_urlsafe(16)
app.secret_key = foo
app.config['UPLOAD_FOLDER'] = 'static/audio_uploads/'
app.config['MAX_CONTENT_LENGTH'] = 250 * 1024 * 1024 # 25MB
app.config['UPLOAD_EXTENSIONS'] = ['.mp3', '.wav']

# Bootstrap-Flask requires this line
bootstrap = Bootstrap(app)
# Flask-WTF requires this line
csrf = CSRFProtect(app)

# Use csrf.exempt to exclude this route from CSRF protection
# Allow CORS for development env
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

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

from flask import render_template, request, jsonify, flash
import time

@app.route('/speech-analysis', methods=['GET', 'POST'])
def speech_analysis():
    form = Upload_Form()
    transcription_results = {}

    if form.validate_on_submit():
        audio = form.file.data
        choice = form.transcription_choice.data
        model_size = form.model_size.data  # Get selected model size
        audio_filename = secure_filename(audio.filename)

        if audio_filename != '':
            file_ext = os.path.splitext(audio_filename)[1]
            if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                flash(f'File Extension {file_ext} not supported', 'error')
                return render_template("speech-analysis.html", form=form)

            audio_name = str(uuid.uuid1()) + "_" + audio_filename
            audio_path = os.path.join(app.config['UPLOAD_FOLDER'], audio_name)
            audio.save(audio_path)

            # Convert the file to WAV using ffmpeg
            wav_filepath = audio_path.rsplit('.', 1)[0] + '.wav'
            convert_to_wav(audio_path, wav_filepath)

            # Instantiate the SpeechTranscriber
            transcriber = SpeechTranscriber()

            if choice == 'cross_comparison_algo':
                # Run all algorithms
                algorithms = ['google', 'whisper-online']  # Add more algorithms if needed
                for algo in algorithms:
                    start_time = time.time()
                    success, text = transcriber.transcribe_audio(wav_filepath, algo, model_size)
                    elapsed_time = time.time() - start_time
                    transcription_results[algo] = {
                        'text': text if success else "Transcription failed",
                        'time': f"{elapsed_time:.2f} seconds"
                    }
            elif choice == 'cross_comparison_model_size':
                # Run all Whisper model sizes
                model_sizes = ['tiny', 'base', 'small', 'medium', 'large', 'turbo']
                for model in model_sizes:
                    start_time = time.time()
                    success, text = transcriber.transcribe_audio(wav_filepath, 'whisper-online', model)
                    elapsed_time = time.time() - start_time
                    transcription_results[model] = {
                        'text': text if success else "Transcription failed",
                        'time': f"{elapsed_time:.2f} seconds"
                    }
            else:
                # Run selected algorithm and model size
                start_time = time.time()
                success, text = transcriber.transcribe_audio(wav_filepath, choice, model_size)
                elapsed_time = time.time() - start_time
                transcription_results[choice] = {
                    'text': text if success else f"Transcription failed!",
                    'time': f"{elapsed_time:.2f} seconds"
                }

    return render_template("speech-analysis.html", form=form, transcription=transcription_results)

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

csrf.exempt(create_user) # extempt this endpoint from csrf token

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

csrf.exempt(delete_user) # extempt this endpoint from csrf token

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

csrf.exempt(save_tapping_result) # extempt this endpoint from csrf token

@app.route('/get-tapping-results/<user_id>', methods=['GET'])
def get_tapping_results(user_id):
    results = Results.query.filter_by(user_id=user_id).all()
    return jsonify([{"date": result.date.strftime('%Y-%m-%d'), "taps": result.taps} for result in results]), 200

@app.route('/process_speech_tasks/<task_type>/<user_id>', methods=['POST'])
def process_speech_tasks(task_type, user_id):

    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Retrieve optional parameters
    transcription_algo = request.form.get('algorithm').lower() # Default to "whisper" ASR
    language_model = request.form.get('modelSize')  # Default to "tiny" model

    # Save the uploaded file
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{user_id}-{timestamp}-{task_type}audiofile"
    original_filepath = os.path.join(f'static/audio_speech_tasks/{task_type}', filename)
    file.save(original_filepath)

    try:
        # Convert the file to WAV using ffmpeg
        wav_filepath = original_filepath.rsplit('.', 1)[0] + '.wav'
        convert_to_wav(original_filepath, wav_filepath)

        if task_type == 'reading':
            # Instantiate the SpeechTranscriber with the selected language model
            transcriber = SpeechTranscriber(language_model)

            # Call transcription function
            success, transcription_or_error = transcriber.transcribe_audio(wav_filepath, transcription_algo)

        elif task_type == 'pataka':
            # Perform feature extraction
            success, transcription_or_error = feature_extraction(wav_filepath)

        else:
            return jsonify({'error': 'Invalid task type', 'reason': f"Unsupported task: {task_type}"}), 422

        # Remove temporary files
        os.remove(original_filepath)

        if success:
            return jsonify({
                'message': 'File uploaded and processed successfully',
                'results': transcription_or_error,
                'taskType': task_type
            }), 200
        else:
            return jsonify({
                'error': 'Processing failed',
                'reason': transcription_or_error
            }), 422

    except Exception as e:
        print(f"Error processing task: {str(e)}")
        return jsonify({'error': 'Internal server error', 'reason': str(e)}), 500

    finally:
        # Ensure original file is cleaned up in case of errors
        if os.path.exists(original_filepath):
            os.remove(original_filepath)

csrf.exempt(process_speech_tasks) # extempt this endpoint from csrf token

def init_db():
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    #init_db()  # Uncomment this if you want to initialize the db every time you run the app
    app.run(debug=True)
