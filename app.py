import speech_recognition as sr
import pyttsx3
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
import torchaudio
import torch
from gtts import gTTS
import os
from pydub import AudioSegment
from datetime import datetime, timedelta
import threading
from plyer import notification

# Set the path to ffmpeg and ffprobe binaries
AudioSegment.ffmpeg = "C:\\Users\\Lenovo india\\Downloads\\ffmpeg-7.0.2-essentials_build\\ffmpeg-7.0.2-essentials_build\\bin\\ffmpeg.exe"
AudioSegment.ffprobe = "C:\\Users\\Lenovo india\\Downloads\\ffmpeg-7.0.2-essentials_build\\ffmpeg-7.0.2-essentials_build\\bin\\ffprobe.exe"

# Load pre-trained STT processor and model
processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base-960h")
model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-base-960h")

# Initialize the recognizer
recognizer = sr.Recognizer()

def convert_to_wav(file_path):
    try:
        audio = AudioSegment.from_file(file_path)
        wav_file_path = file_path.rsplit('.', 1)[0] + '.wav'
        audio.export(wav_file_path, format='wav')
        return wav_file_path
    except Exception as e:
        print(f"Error in converting audio to WAV: {str(e)}")
        return None

def transcribe_audio(file_path):
    try:
        if not file_path.endswith('.wav'):
            file_path = convert_to_wav(file_path)
            if file_path is None:
                return "Error in converting audio file to WAV format."

        audio_input, _ = torchaudio.load(file_path)
        input_values = processor(audio_input.squeeze().numpy(), return_tensors="pt", padding=True).input_values
        with torch.no_grad():
            logits = model(input_values).logits
        predicted_ids = torch.argmax(logits, dim=-1)
        transcription = processor.batch_decode(predicted_ids)[0]
        return transcription
    except Exception as e:
        return f"Error in transcribing audio: {str(e)}"

def text_to_speech_gtts(text, output_file):
    try:
        tts = gTTS(text=text, lang='en')
        tts.save(output_file)
        if os.name == 'nt':  # Windows
            os.system(f"start {output_file}")
        else:  # MacOS or Linux
            os.system(f"open {output_file}" if os.name == 'posix' else f"xdg-open {output_file}")
    except Exception as e:
        print(f"Error in text-to-speech conversion: {str(e)}")

def speak_text_pyttsx3(command):
    try:
        engine = pyttsx3.init()
        engine.say(command)
        engine.runAndWait()
    except Exception as e:
        print(f"Error in text-to-speech using pyttsx3: {str(e)}")

def notify_user(message):
    try:
        notification.notify(
            title="Reminder",
            message=message,
            timeout=10
        )
    except Exception as e:
        print(f"Error in notification: {str(e)}")

def set_reminder(message, reminder_time):
    def reminder_thread():
        current_time = datetime.now()
        time_diff = (reminder_time - current_time).total_seconds()
        if time_diff > 0:
            print(f"Reminder set for {reminder_time}. You will be notified in {time_diff} seconds.")
            threading.Timer(time_diff, notify_user, args=(message,)).start()
        else:
            print("Reminder time must be in the future.")

    thread = threading.Thread(target=reminder_thread)
    thread.start()

def set_reminder_voice():
    print("Please speak your reminder details...")
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        # Recognize speech using Google STT
        reminder_details = recognizer.recognize_google(audio)
        print(f"Received reminder details: {reminder_details}")

        # Example: Setting a static reminder for 1 minute later
        reminder_time = datetime.now() + timedelta(minutes=1)  # Modify this to parse actual date and time
        set_reminder(reminder_details, reminder_time)
        print("Reminder set successfully by voice.")
    except Exception as e:
        print(f"Failed to set reminder: {str(e)}")

def main():
    while True:
        print("\n1. Convert Speech to Text")
        print("2. Convert Text to Speech")
        print("3. Set Reminder")
        print("4. Set Reminder by Voice")
        print("5. Exit")
        choice = input("Enter choice (1/2/3/4/5): ")

        if choice == '1':
            print("Speak now...")
            try:
                with sr.Microphone() as source:
                    recognizer.adjust_for_ambient_noise(source, duration=0.2)
                    audio = recognizer.listen(source)
                    text = recognizer.recognize_google(audio)
                    text = text.lower()
                    print(f"You said: {text}")
                    speak_text_pyttsx3(text)
            except sr.RequestError as e:
                print(f"Could not request results; {e}")
            except sr.UnknownValueError:
                print("Unknown error occurred")

        elif choice == '2':
            text = input("Enter text to convert to speech: ")
            output_file = input("Enter output file name (e.g., output.mp3): ")
            text_to_speech_gtts(text, output_file)

        elif choice == '3':
            message = input("Enter reminder message: ")
            reminder_time_str = input("Enter reminder time (YYYY-MM-DD HH:MM:SS): ")
            try:
                reminder_time = datetime.strptime(reminder_time_str, "%Y-%m-%d %H:%M:%S")
                set_reminder(message, reminder_time)
            except ValueError:
                print("Invalid date format. Please enter the date and time in the format: YYYY-MM-DD HH:MM:SS")

        elif choice == '4':
            set_reminder_voice()

        elif choice == '5':
            print("Exiting...")
            break

        else:
            print("Invalid choice. Please enter 1, 2, 3, 4, or 5.")

if __name__ == "__main__":
    main()
4