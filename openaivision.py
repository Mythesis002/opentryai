from flask import Flask, request, jsonify
from flask_cors import CORS
import cloudinary
import cloudinary.uploader
import requests

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Cloudinary Credentials
cloudinary.config(
    cloud_name="dkr5qwdjd",  # Replace with your Cloudinary Cloud Name
    api_key="797349366477678",  # Replace with your Cloudinary API Key
    api_secret="9HUrfG_i566NzrCZUVxKyCHTG9U"  # Replace with your Cloudinary API Secret
)

# RapidAPI credentials
RAPIDAPI_KEY = "c66b66fd5fmsh2d1f2d4c5d0a073p17161ajsnb75f8dbbac1d"
RAPIDAPI_HOST = "chatgpt-vision1.p.rapidapi.com"


@app.route('/upload_and_process', methods=['POST'])
def upload_and_process_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No image part in the request'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        # Step 1: Upload Image to Cloudinary
        upload_result = cloudinary.uploader.upload(file, folder="Mythesis_images")
        if 'secure_url' not in upload_result:
            return jsonify({'error': 'Failed to upload image to Cloudinary'}), 500

        original_image_url = upload_result['secure_url']
        public_id = upload_result['public_id']

        print("Original Image URL:", original_image_url)

        # Step 2: Enhance Image using Cloudinary
        enhanced_image_url = cloudinary.CloudinaryImage(public_id).build_url(transformation=[
            {'effect': 'improve'}  # Enhance image using 'improve' effect
        ])
        print("Enhanced Image URL:", enhanced_image_url)

        # Step 3: Send Enhanced Image URL to RapidAPI for Text Extraction
        payload = {
            "messages": [
                {
                    "role": "user",
                    "content": "Analyze the image and extract all details about the product. Describe its brand name, visible logos, colors, text, patterns, materials, and textures. Include all written information on the product, such as fonts, font sizes, and styles. Identify design elements, shapes, and any distinguishing features, ensuring the description is accurate and comprehensive. Avoid mentioning location, environment,background or lighting.",
                    "img_url": enhanced_image_url
                }
            ]
        }

        headers = {
            "x-rapidapi-key": RAPIDAPI_KEY,
            "x-rapidapi-host": RAPIDAPI_HOST,
            "Content-Type": "application/json"
        }

        response = requests.post("https://chatgpt-vision1.p.rapidapi.com/matagvision", json=payload, headers=headers)

        if response.status_code == 200:
            result = response.json()
            print("API Response:", result)

            return jsonify({
                "original_image_url": original_image_url,
                "enhanced_image_url": enhanced_image_url,
                "api_response": result
            }), 200
        else:
            return jsonify({'error': 'Failed to process image via RapidAPI', 'details': response.text}), 500

    except Exception as e:
        print(f"Exception occurred: {e}")  # Print exception for debugging
        return jsonify({'error': 'An error occurred: ' + str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
