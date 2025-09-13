import speech_recognition as sr
import pyttsx3
from gtts import gTTS
import io
import tempfile
import os
from typing import Optional, Tuple
import whisper

class VoiceHandler:
    """
    Handles speech-to-text and text-to-speech functionality for the chatbot.
    """

    def __init__(self, tts_engine: str = "pyttsx3", stt_engine: str = "whisper"):
        """
        Initialize the voice handler.

        Args:
            tts_engine: Text-to-speech engine ("pyttsx3" or "gtts")
            stt_engine: Speech-to-text engine ("whisper" or "google")
        """
        self.tts_engine = tts_engine
        self.stt_engine = stt_engine

        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        # Initialize TTS engines
        if tts_engine == "pyttsx3":
            self._init_pyttsx3()

        # Initialize Whisper model for better speech recognition
        if stt_engine == "whisper":
            self._init_whisper()

        # Calibrate microphone for ambient noise
        self._calibrate_microphone()

    def _init_pyttsx3(self):
        """Initialize pyttsx3 TTS engine."""
        try:
            self.tts_engine_obj = pyttsx3.init()

            # Configure voice settings
            voices = self.tts_engine_obj.getProperty('voices')
            if voices:
                # Try to set a female voice for nutrition coach personality
                for voice in voices:
                    if 'female' in voice.name.lower() or 'woman' in voice.name.lower():
                        self.tts_engine_obj.setProperty('voice', voice.id)
                        break
                else:
                    # Use first available voice
                    self.tts_engine_obj.setProperty('voice', voices[0].id)

            # Set speech rate and volume
            self.tts_engine_obj.setProperty('rate', 180)  # Words per minute
            self.tts_engine_obj.setProperty('volume', 0.9)

            print("✅ pyttsx3 TTS engine initialized")
        except Exception as e:
            print(f"⚠️ Error initializing pyttsx3: {e}")
            self.tts_engine = "gtts"

    def _init_whisper(self):
        """Initialize Whisper model for speech recognition."""
        try:
            # Use small model for faster processing while maintaining accuracy
            self.whisper_model = whisper.load_model("base")
            print("✅ Whisper model loaded successfully")
        except Exception as e:
            print(f"⚠️ Error loading Whisper model: {e}")
            print("🔄 Falling back to Google Speech Recognition")
            self.stt_engine = "google"
            self.whisper_model = None

    def _calibrate_microphone(self):
        """Calibrate microphone for ambient noise."""
        try:
            with self.microphone as source:
                print("🎤 Calibrating microphone for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                print("✅ Microphone calibrated")
        except Exception as e:
            print(f"⚠️ Microphone calibration error: {e}")

    def listen_for_speech(self, timeout: int = 10, phrase_time_limit: int = 15) -> Tuple[Optional[str], bool]:
        """
        Listen for speech input and convert to text.

        Args:
            timeout: Maximum time to wait for speech to start
            phrase_time_limit: Maximum time for a single phrase

        Returns:
            Tuple of (transcribed_text, success)
        """
        try:
            with self.microphone as source:
                print("🎤 Listening for speech...")

                # Listen for audio
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )

                print("🔄 Processing speech...")

                # Use selected STT engine
                if self.stt_engine == "whisper" and self.whisper_model:
                    return self._transcribe_with_whisper(audio)
                else:
                    return self._transcribe_with_google(audio)

        except sr.WaitTimeoutError:
            return None, False
        except sr.RequestError as e:
            print(f"❌ Speech recognition service error: {e}")
            return None, False
        except Exception as e:
            print(f"❌ Unexpected error in speech recognition: {e}")
            return None, False

    def _transcribe_with_whisper(self, audio: sr.AudioData) -> Tuple[Optional[str], bool]:
        """
        Transcribe audio using Whisper model.

        Args:
            audio: Audio data from speech recognition

        Returns:
            Tuple of (transcribed_text, success)
        """
        try:
            # Convert audio to format Whisper expects
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
                temp_audio.write(audio.get_wav_data())
                temp_audio_path = temp_audio.name

            # Transcribe with Whisper
            result = self.whisper_model.transcribe(temp_audio_path)
            text = result["text"].strip()

            # Clean up temp file
            os.unlink(temp_audio_path)

            if text:
                print(f"🎯 Whisper transcription: '{text}'")
                return text, True
            else:
                return None, False

        except Exception as e:
            print(f"❌ Whisper transcription error: {e}")
            return None, False

    def _transcribe_with_google(self, audio: sr.AudioData) -> Tuple[Optional[str], bool]:
        """
        Transcribe audio using Google Speech Recognition.

        Args:
            audio: Audio data from speech recognition

        Returns:
            Tuple of (transcribed_text, success)
        """
        try:
            text = self.recognizer.recognize_google(audio)
            if text:
                print(f"🎯 Google transcription: '{text}'")
                return text, True
            else:
                return None, False
        except sr.UnknownValueError:
            print("❌ Could not understand the speech")
            return None, False
        except sr.RequestError as e:
            print(f"❌ Google Speech Recognition error: {e}")
            return None, False

    def text_to_speech(self, text: str, save_to_file: bool = False) -> Optional[str]:
        """
        Convert text to speech.

        Args:
            text: Text to convert to speech
            save_to_file: Whether to save audio to a temporary file

        Returns:
            Path to audio file if save_to_file is True, None otherwise
        """
        if self.tts_engine == "pyttsx3":
            return self._speak_with_pyttsx3(text, save_to_file)
        else:
            return self._speak_with_gtts(text, save_to_file)

    def _speak_with_pyttsx3(self, text: str, save_to_file: bool = False) -> Optional[str]:
        """
        Generate speech using pyttsx3.

        Args:
            text: Text to speak
            save_to_file: Whether to save to file

        Returns:
            File path if saved, None otherwise
        """
        try:
            if save_to_file:
                # Save to temporary file
                temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
                self.tts_engine_obj.save_to_file(text, temp_file.name)
                self.tts_engine_obj.runAndWait()
                return temp_file.name
            else:
                # Speak directly
                self.tts_engine_obj.say(text)
                self.tts_engine_obj.runAndWait()
                return None

        except Exception as e:
            print(f"❌ pyttsx3 TTS error: {e}")
            return None

    def _speak_with_gtts(self, text: str, save_to_file: bool = False) -> Optional[str]:
        """
        Generate speech using Google Text-to-Speech.

        Args:
            text: Text to speak
            save_to_file: Whether to save to file

        Returns:
            File path if saved, None otherwise
        """
        try:
            # Create gTTS object
            tts = gTTS(text=text, lang='en', slow=False)

            if save_to_file:
                # Save to temporary file
                temp_file = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
                tts.save(temp_file.name)
                return temp_file.name
            else:
                # Play directly (requires additional audio player)
                fp = io.BytesIO()
                tts.write_to_fp(fp)
                fp.seek(0)

                # Note: Direct playback would require additional audio library
                # For now, we'll save to temp file even if not requested
                temp_file = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
                tts.save(temp_file.name)
                return temp_file.name

        except Exception as e:
            print(f"❌ gTTS error: {e}")
            return None

    def is_microphone_available(self) -> bool:
        """
        Check if microphone is available for recording.

        Returns:
            True if microphone is available, False otherwise
        """
        try:
            with self.microphone as source:
                pass
            return True
        except Exception:
            return False

    def get_available_voices(self) -> list:
        """
        Get list of available TTS voices.

        Returns:
            List of available voice information
        """
        if self.tts_engine == "pyttsx3" and hasattr(self, 'tts_engine_obj'):
            try:
                voices = self.tts_engine_obj.getProperty('voices')
                return [{"id": voice.id, "name": voice.name} for voice in voices] if voices else []
            except Exception:
                return []
        else:
            # gTTS doesn't have multiple voices
            return [{"id": "gtts_en", "name": "Google TTS English"}]

    def set_voice(self, voice_id: str) -> bool:
        """
        Set the TTS voice.

        Args:
            voice_id: ID of the voice to use

        Returns:
            True if voice was set successfully, False otherwise
        """
        if self.tts_engine == "pyttsx3" and hasattr(self, 'tts_engine_obj'):
            try:
                self.tts_engine_obj.setProperty('voice', voice_id)
                return True
            except Exception:
                return False
        return False

    def set_speech_rate(self, rate: int) -> bool:
        """
        Set the speech rate for TTS.

        Args:
            rate: Speech rate in words per minute

        Returns:
            True if rate was set successfully, False otherwise
        """
        if self.tts_engine == "pyttsx3" and hasattr(self, 'tts_engine_obj'):
            try:
                self.tts_engine_obj.setProperty('rate', max(50, min(300, rate)))
                return True
            except Exception:
                return False
        return False