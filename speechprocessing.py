import speech_recognition as sr
import ffmpeg

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

def feature_extraction(file_path):
    try:
        # Recognize (convert from speech to text) using the default API key
        text = "This worked well"
        return (True, text)
    except sr.UnknownValueError:
        # API was unable to understand the audio
        print("Feature Extraction failed. Try again.")
        return (False, "Feature Extraction failed. Try again.")
    except sr.RequestError as e:
        # Request failed
        return (False, f"Feature Extraction failed: {e}")

