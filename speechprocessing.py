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
    def __init__(self, language_model):
        self.recognizer = sr.Recognizer()
        self.whisper_model = whisper.load_model(language_model)  # Choose the appropriate model size
    def transcribe_audio(self, file_path, algorithm):
        with sr.AudioFile(file_path) as source:
            self.recognizer.adjust_for_ambient_noise(source)
            audio_data = self.recognizer.record(source)

        algorithm = algorithm.lower()
        if algorithm == 'whisper-offline':
            return self.transcribe_whisper_offline(audio_data)
        elif algorithm == 'whisperx-offline':
            return self.transcribe_whisperx(audio_data)
        elif algorithm == 'whisper-online':
            return self.transcribe_whisper_online(file_path)
        elif algorithm == 'google':
            return self.transcribe_google(audio_data)
        elif algorithm == 'sphinx':
            return self.transcribe_sphinx(audio_data)
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

    # Implementation for Whisper Online
    def transcribe_whisper_online(self, file_path):
        try:
            result = self.whisper_model.transcribe(file_path)
            return (True, result['text'])
        except Exception as e:
            return (False, f"Whisper Online transcription failed; {e}")

    # Implementation of Whisper Offline
    def transcribe_whisper_offline(self, audio_data):
        try:
            text = self.recognizer.recognize_google(audio_data)
            return (True, text)
        except sr.UnknownValueError:
            return (False, "Whisper Speech Recognition could not understand audio")
        except sr.RequestError as e:
            return (False, f"Could not request results from Whisper Speech Recognition service; {e}")
    # Implementation of WhisperX
    def transcribe_whisperx(self, file_path):
        try:
            result = self.whisper_model.transcribe(file_path)
            return (True, result['text'])
        except Exception as e:
            return (False, f"WhisperX transcription failed; {e}")

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

