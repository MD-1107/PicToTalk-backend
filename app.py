from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from io import BytesIO
import base64
from PIL import Image
from io import BytesIO
from google.cloud import vision
from google.cloud import translate_v2 as translate
from google.cloud import texttospeech_v1


app = Flask(__name__)
CORS(app, resources={r"/process_image": {"origins": "http://localhost:3000"}})

# Ensure the folder for uploaded images exists
if not os.path.exists("uploads"):
    os.makedirs("uploads")


@app.route("/process_image", methods=["POST"])
def process_image():
   

def analyze_translate_and_speak(image_file, target_language='en'):

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "cloudcomputing-398709-d793149a510a.json"
    # Initialize the Vision API client
    vision_client = vision.ImageAnnotatorClient()
    print(vision_client)
    # Read the image content from the provided image file
    content = image_file.read()

    print(content)
    # Create an image object
    image = vision.Image(content=content)

    print(target_language)

    # Use the Vision API to detect text in the image
    response = vision_client.text_detection(image=image)

    print(response)

    # Extract and display the detected text
    detected_text = ''
    if response.text_annotations:
        detected_text = response.text_annotations[0].description

    # Initialize the Translation API client
    translate_client = translate.Client()

    # Translate the detected text to the desired language
    translation = translate_client.translate(detected_text, target_language=target_language)

    # Initialize the Text-to-Speech API client
    text_to_speech_client = texttospeech_v1.TextToSpeechClient()

    # Specify the voice parameters
    voice = texttospeech_v1.VoiceSelectionParams(
        language_code=target_language,
        name=f"{target_language}-US-Wavenet-D",  # Adjust the voice name for your desired language and gender
    )

    # Specify the audio parameters
    audio_config = texttospeech_v1.AudioConfig(
        audio_encoding=texttospeech_v1.AudioEncoding.LINEAR16
    )

    # Synthesize speech from the translated text
    synthesis_input = texttospeech_v1.SynthesisInput(text=translation['translatedText'])
    response = text_to_speech_client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )

    # Save the synthesized speech to an audio file (e.g., in-memory bytes)
    audio_content = response.audio_content

    # Create a dictionary to store all the information
    result = {
        'input': detected_text,
        'translatedText': translation['translatedText'],
        'detectedSourceLanguage': translation['detectedSourceLanguage'],
        'audio': audio_content  # Store audio content
    }

    print(detected_text)
    print(translation['translatedText'])
    print(translation['detectedSourceLanguage'])

    return result


if __name__ == "__main__":
    app.run(debug=True)
