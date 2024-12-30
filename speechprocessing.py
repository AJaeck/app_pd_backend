import speech_recognition as sr
import ffmpeg
import whisper
import os

def convert_to_wav(input_path, output_path):
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file does not exist: {input_path}")

    try:
        ffmpeg.input(input_path).output(output_path).run()
    except Exception as e:
        raise RuntimeError(f"FFmpeg conversion failed: {e}")

class SpeechTranscriber:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.whisper_model = whisper.load_model("base")  # Choose the appropriate model size
    def transcribe_audio(self, file_path, algorithm):
        with sr.AudioFile(file_path) as source:
            self.recognizer.adjust_for_ambient_noise(source)
            audio_data = self.recognizer.record(source)

        algorithm = algorithm.lower()
        if algorithm == 'google':
            return self.transcribe_google(audio_data)
        elif algorithm == 'google_cloud':
            return self.transcribe_google_cloud(audio_data)
        elif algorithm == 'wit':
            return self.transcribe_wit(audio_data)
        elif algorithm == 'bing':
            return self.transcribe_bing(audio_data)
        elif algorithm == 'houndify':
            return self.transcribe_houndify(audio_data)
        elif algorithm == 'ibm':
            return self.transcribe_ibm(audio_data)
        elif algorithm == 'sphinx':
            return self.transcribe_sphinx(audio_data)
        elif algorithm == 'whisper':
            return self.transcribe_whisper(file_path)
        else:
            return (False, "Unsupported transcription service")

    # Example implementation for Google
    def transcribe_google(self, audio_data):
        try:
            text = self.recognizer.recognize_google(audio_data)
            return (True, text)
        except sr.UnknownValueError:
            return (False, "Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            return (False, f"Could not request results from Google Speech Recognition service; {e}")

    # Implementation for Whisper
    def transcribe_whisper(self, file_path):
        try:
            result = self.whisper_model.transcribe(file_path)
            return (True, result['text'])
        except Exception as e:
            return (False, f"Whisper transcription failed; {e}")

    # Add additional methods for other services...

def feature_extraction(file_path):
    try:
        # Recognize (convert from speech to text) using the default API key
        text = "Feature Extraction coming soon"
        return (True, text)
    except sr.UnknownValueError:
        # API was unable to understand the audio
        print("Feature Extraction failed. Try again.")
        return (False, "Feature Extraction failed. Try again.")
    except sr.RequestError as e:
        # Request failed
        return (False, f"Feature Extraction failed: {e}")

