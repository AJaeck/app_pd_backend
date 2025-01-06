import os
import json
import ffmpeg
import whisper_timestamped as whisper
import whisperx

def convert_to_wav(input_path, output_path):
    """
    Convert audio file to WAV format with specified parameters.

    Args:
        input_path (str): Path to the input audio file.
        output_path (str): Path to save the converted WAV file.

    Raises:
        FileNotFoundError: If the input file does not exist.
        RuntimeError: If FFmpeg conversion fails.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file does not exist: {input_path}")
    try:
        ffmpeg.input(input_path).output(output_path, ar=16000, ac=1, format='wav').run()
    except Exception as e:
        raise RuntimeError(f"FFmpeg conversion failed: {e}")

class SpeechTranscriber:

    def transcribe_audio(self, file_path, algorithm, model_size=None):
        """
        Transcribe audio using the specified algorithm.

        Args:
            file_path (str): Path to the audio file.
            algorithm (str): Transcription algorithm to use.
            model_size (str, optional): Model size for Whisper. Defaults to None.

        Returns:
            tuple: (success (bool), transcription or error message)
        """
        if algorithm == 'whisper':
            return self.transcribe_whisper(file_path, model_size)
        elif algorithm == 'whisperx':
            return self.transcribe_whisperx(file_path, model_size)
        else:
            return (False, "Unsupported transcription service")

    def transcribe_whisper(self, file_path, model_size):
        """
        Transcribe audio using vanilla Whisper from OpenAI.

        Args:
            file_path (str): Path to the audio file.
            model_size (str): Model size for Whisper.

        Returns:
            tuple: (success (bool), transcription or error message)
        """
        try:
            model_size = model_size or "base"
            model = whisper.load_model(model_size)
            result = whisper.transcribe(model, file_path, language="de")
            return True, result['text']
        except Exception as e:
            return False, f"Whisper Online transcription failed: {e}"

    def transcribe_whisperx(self, file_path, model_size):
        """
        Transcribe audio using WhisperX.

        Args:
            file_path (str): Path to the audio file.

        Returns:
            tuple: (success (bool), transcription or error message)
        """
        try:
            device = "cpu"
            batch_size = 16  # reduce if low on GPU mem
            compute_type = "int8"  # change to "int8" if low on GPU mem (may reduce accuracy)
            # 1. Transcribe with original whisper (batched)
            model = whisperx.load_model(model_size, device, compute_type=compute_type, language="de")
            audio = whisperx.load_audio(file_path)
            result = model.transcribe(audio, batch_size=batch_size)

            # Combine all texts into one
            full_text = " ".join(segment['text'] for segment in result['segments'])
            print(full_text)  # before

            # 2. Align whisper output
            model_a, metadata = whisperx.load_align_model(language_code="de", device=device)
            result = whisperx.align(result["segments"], model_a, metadata, audio, device,
                                    return_char_alignments=False)
            #print(result["segments"])  # after alignment
            return True, full_text
        except Exception as e:
            return False, f"WhisperX transcription failed: {e}"


def feature_extraction(file_path):
    """
    Placeholder for feature extraction.

    Args:
        file_path (str): Path to the audio file.

    Returns:
        tuple: (success (bool), extracted features or error message)
    """
    try:
        # Placeholder text for demonstration purposes
        return True, "Feature extraction coming soon."
    except Exception as e:
        return False, f"Feature extraction failed: {e}"
