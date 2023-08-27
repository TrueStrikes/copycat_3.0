from PIL import Image
import pytesseract

# Path to your Tesseract executable (update this to your Tesseract installation path)
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\moore_nieszk\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

# Function to extract text from an image file
def extract_text_from_image(image_path):
    try:
        # Open the image using Pillow (PIL)
        img = Image.open(image_path)

        # Use Tesseract to extract text from the image
        text = pytesseract.image_to_string(img, lang='eng')  # Use 'eng' for English language

        return text
    except Exception as e:
        print(f"Error extracting text: {str(e)}")
        return None

# Provide the path to the image file you want to process
image_path = 'Code_Generation.png'  # Update with your image file path

# Extract text from the image
extracted_text = extract_text_from_image(image_path)

# Print the extracted text
if extracted_text:
    print("Extracted Text:")
    print(extracted_text)
else:
    print("No text found in the image.")
