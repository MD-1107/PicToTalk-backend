from flask import Flask, jsonify, request
from flask_cors import CORS
import math
from bson.json_util import dumps
import json
import html
import os

# Imports the Google Cloud client libraries
from google.api_core.exceptions import AlreadyExists
from google.cloud import texttospeech
from google.cloud import translate_v3beta1 as translate
from google.cloud import vision
from google.cloud import vision

app = Flask(__name__)
CORS(app)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "cloudcomputing-398709-d793149a510a.json"


def analyze_image(image_path):
    """Analyzes the provided image file using specific feature types."""

    # Initialize the Vision API client
    client = vision.ImageAnnotatorClient()

    # Read the image file
    with open(image_path, "rb") as image_file:
        content = image_file.read()

    # Create an image object
    image = vision.Image(content=content)

    # Define the specific feature types
    features = [
        vision.Feature(type=vision.Feature.Type.LABEL_DETECTION),
        vision.Feature(type=vision.Feature.Type.TEXT_DETECTION)
    ]

    # Use the Vision API to analyze the image with the specified features
    response = client.annotate_image({
        'image': image,
        'features': features
    })

    # Extract and display the results for the specified feature types
    if response.label_annotations:
        print("\nLabels (Objects):")
        for label in response.label_annotations:
            print(label.description)

    if response.text_annotations:
        print("\nDetected Text:")
        for text in response.text_annotations:
            print(f'"{text.description}"')

# Provide the image file name as a parameter to the function
image_file_name = "french_menu.jpg"  # Replace with the actual image file name
analyze_image(image_file_name)
