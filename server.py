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
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app, resources={r"/process_image": {"origins": "http://localhost:3000"}})
# Configuration for file uploads
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the "uploads" folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "cloudcomputing-398709-d793149a510a.json"


@app.route('/process_image', methods=['POST'])
def process_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No file part'})

    image = request.files['image']

    if image.filename == '':
        return jsonify({'error': 'No selected file'})

    if image:
        filename = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        target_language = request.form.get("target_language", "en")
        
        # Perform image processing here (e.g., using a library like Tesseract.js)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        result = analyze_translate_and_speak(image_path, target_language)
        
        # You can return any results you want to the frontend
        translated_text = result['translatedText']
        audio_file = result['audio']

        return jsonify({'translatedText': translated_text, 'audioFile': audio_file})


def analyze_translate_and_speak(image_content, target_language='en'):
    
    vision_client = vision.ImageAnnotatorClient()

    # Read the image file
    with open(image_content, "rb") as image_file:
        content = image_file.read()

    # Create an image object
    image = vision.Image(content=content)

    # Use the Vision API to detect text in the image
    response = vision_client.text_detection(image=image)

    # Extract and display the detected text
    detected_text = ''
    if response.text_annotations:
        detected_text = response.text_annotations[0].description
        print("\nDetected Text:")
        print(f'"{detected_text}"')

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
        'audio': base64.b64encode(audio_content).decode('utf-8')
    }

    return result

if __name__ == '__main__':
    app.run(debug=True)
