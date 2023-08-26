import requests
import json
import os
import time
import threading
import re
import pygame
import colorama
import clipboard
import pytesseract
from PIL import Image

# Initialize Pygame
pygame.init()

# Initialize colorama
colorama.init()

# Define custom Tesseract OCR configurations for better accuracy
custom_ocr_config = r'--oem 3 --psm 6 -l eng'  # Example: Use English language

# Set to keep track of retrieved message IDs and user messages
retrieved_message_ids = set()
user_messages = set()

# Set to keep track of processed message IDs
processed_message_ids = set()

# Variable to indicate if the script is running
running = True

def display_message(channelid, message):
    message_id = message.get('id')
    if message_id not in retrieved_message_ids:
        retrieved_message_ids.add(message_id)
        author_id = message.get('author', {}).get('id')
        content = message.get('content')
        if author_id in target_user_ids and content not in user_messages:
            print(colorama.Fore.YELLOW + "Message:")
            print(content)
            print(colorama.Style.RESET_ALL)

            # Check if the content starts with "# "
            if content.startswith("# "):
                content = content[2:]  # Remove "# " from the beginning

            copy_to_clipboard(content)  # Copy the message content to the clipboard
            user_messages.add(content)
            play_sound("t.mp3")  # Play the sound "t.mp3"

    # Process images in the message
    if author_id in target_user_ids:
        download_and_process_images(message)

def retrieve_latest_messages(channelid):
    headers = {
        'authorization': bot_token
    }
    params = {
        'limit': 1  # Update to retrieve the last 5 messages
    }
    r = requests.get(f'https://discord.com/api/v8/channels/{channelid}/messages', headers=headers, params=params)
    try:
        messages = json.loads(r.text)
    except json.JSONDecodeError as e:
        print("JSON decode error:", e)
        return []

    if not isinstance(messages, list) or len(messages) == 0:
        return []

    return messages

def play_sound(sound_filename):
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(sound_filename)
        pygame.mixer.music.play()
        time.sleep(1)  # Give it some time to play the sound
    except Exception as e:
        print("Error playing sound:", e)

# Copy the message content to the clipboard
def copy_to_clipboard(content):
    clipboard.copy(content)

# Clear the console and print "Watching" in bright yellow
def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(colorama.Fore.YELLOW + "Watching")
    print(colorama.Style.RESET_ALL)

# Function to preprocess an image before OCR
def preprocess_image(image):
    # Add any image preprocessing steps here (e.g., resizing, thresholding)
    return image

# Function to extract text from an image using Tesseract OCR
def extract_text_from_image(image_path):
    try:
        pytesseract.pytesseract.tesseract_cmd = tesseract_path  # Use the custom Tesseract path
        # Load the image using PIL (Pillow)
        image = Image.open(image_path)

        # Perform image preprocessing (resizing, thresholding, etc.) before passing it to Tesseract
        preprocessed_image = preprocess_image(image)

        # Use Tesseract with custom options
        text = pytesseract.image_to_string(preprocessed_image, config=custom_ocr_config)

        return text.strip()
    except Exception as e:
        print(f"Error extracting text from image: {e}")
        return ""

# Function to download and process images in a message
def download_and_process_images(message):
    attachments = message.get('attachments', [])
    for attachment in attachments:
        image_url = attachment.get('url')
        if image_url:
            image_filename = os.path.basename(image_url)
            image_path = os.path.join('images', image_filename)

            # Download the image
            download_image(image_url, image_path)

            # Extract text from the image using Tesseract OCR
            extracted_text = extract_text_from_image(image_path)

            # If text was extracted, copy it to the clipboard
            if extracted_text:
                copy_to_clipboard(extracted_text)
                print(f"Extracted text from image: {extracted_text}")

# Function to download an image from a URL
def download_image(image_url, image_path):
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            with open(image_path, 'wb') as image_file:
                image_file.write(response.content)
    except Exception as e:
        print(f"Error downloading image: {e}")

# Read the filename of the JSON file from config.json
config_filename = "config.json"
try:
    with open(config_filename, 'r') as config_file:
        config_data = json.load(config_file)
except (FileNotFoundError, json.JSONDecodeError):
    config_data = {}  # If there's an error or the file doesn't exist, initialize an empty config dictionary

# Load the settings from the specified file
settings_filename = config_data.get("config_filename", "settings.json")
tesseract_path = config_data.get("tesseract_path", "")
try:
    with open(settings_filename, 'r') as settings_file:
        settings_data = json.load(settings_file)
        bot_token = settings_data.get("bot_token", "")
        target_user_ids = settings_data.get("target_user_ids", [])
        target_channels = settings_data.get("target_channels", [])
except (FileNotFoundError, json.JSONDecodeError):
    bot_token = ""
    target_user_ids = []
    target_channels = []

# Set the loop to run indefinitely
while True:
    if running and bot_token and target_user_ids and target_channels:
        headers = {
            'authorization': bot_token
        }

        for channel_id in target_channels:
            latest_messages = retrieve_latest_messages(channel_id)
            if latest_messages:
                for message in latest_messages:
                    if message['id'] not in processed_message_ids:
                        display_message(channel_id, message)
                        processed_message_ids.add(message['id'])

    time.sleep(0.05)  # Add a wait time of 0.05 seconds before the next iteration
