import requests
import re
from huggingface_hub import InferenceClient
from PIL import Image, ImageDraw, ImageFont
import cloudinary
import cloudinary.uploader
import cloudinary.api
import io
import numpy as np
import os
import time
import schedule
import datetime

# 🔹 Instagram Credentials
ACCESS_TOKEN = "EAAWYAavlRa4BO8OE7Ho6gtx4a85DRgNMc59ZCpAdsHXNJnbZABREkXovZCKnbo9AlupOjbJ5xYSTBrMIMTVtu9n530I3ZC2JZBuZBpCDzHyjI7ngh8EtCrSvUho9VGZB9Xdxt5JLGNrHwfDsSIqtvxFjefG2t2JsgJpqfZAMCjO8AURp79mU0WAaLA7R"
INSTAGRAM_ACCOUNT_ID = "17841468918737662"
INSTAGRAM_NICHE_ACCOUNT = "evolving.ai"

def post_reel():
    """Uploads and posts an Instagram Reel automatically."""
    print(f"📅 Running at: {datetime.datetime.now()}")

    # 🔹 1. Get Instagram Caption
    url = "https://instagram230.p.rapidapi.com/user/posts"
    querystring = {"username": INSTAGRAM_NICHE_ACCOUNT}
    headers = {
	      "x-rapidapi-key": "628e474f5amsh0457d8f1b4fb50cp16b75cjsn70408f276e9b",
	      "x-rapidapi-host": "instagram230.p.rapidapi.com",
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers, params=querystring)

    data = response.json()
    if 'items' in data and len(data['items']) > 0:
        # Access the caption text from the first item in the 'items' list
        caption_text = data['items'][0]['caption']['text']
    else:
        # Handle the case where the expected structure is not found
        print("Error: Unexpected response structure or empty 'items' list.")
        print(data)  # Print the response for debugging

    # 🔹 2. Generate Headline & Image Prompt
    url = "https://chatgpt-42.p.rapidapi.com/gpt4"
    payload = {
        "messages": [
            {
                "role": "system",
                "content":
                "You are an AI assistant that specializes in generating high-quality Instagram post elements. "
                "For any given caption, you must return:\n"
                "1️⃣ **Instagram Headline**: A detailed short, attention-grabbing headline (min 2lines).\n"
                "2️⃣ **Image Prompt**: A detailed description of the ideal AI-generated image.\n\n"
                "Format your response **exactly** like this:\n"
                "**Headline:** Your catchy headline here\n"
                "**Image Prompt:** Your detailed image description here"
            },
            {
                "role": "user",
                "content": caption_text
            }
        ],
        "web_access": False
    }
    headers = {
        "x-rapidapi-key": "c4149d7f42msh169b1ac1d7c079ep17cebfjsn882b5a92dacd",
        "x-rapidapi-host": "chatgpt-42.p.rapidapi.com",
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=payload, headers=headers)
    response_data = response.json()
    result_text = response_data.get("result", "").strip()



 
    headline_pattern = r'\*\*Headline:\*\*\s*(.+)'
    image_prompt_pattern = r'\*\*Image Prompt:\*\*\s*(.+)'

    headline_match = re.search(headline_pattern, result_text)
    image_prompt_match = re.search(image_prompt_pattern, result_text)

    headline = headline_match.group(1).strip() if headline_match else "No headline found"
    image_prompt = image_prompt_match.group(1).strip() if image_prompt_match else "No image prompt found"


    # 🔹 3. Generate Image & Create Video
    client = InferenceClient(token="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")
    model = "black-forest-labs/FLUX.1-dev"
    image = client.text_to_image(image_prompt, model=model)





    # 🔹 5. Upload Video to Cloudinary
    cloudinary.config(
        cloud_name="dkr5qwdjd",
        api_key="797349366477678",
        api_secret="9HUrfG_i566NzrCZUVxKyCHTG9U"
    )
    # Convert the PIL Image to bytes
    image_bytes = io.BytesIO()
    image.save(image_bytes, format='PNG')  # Or whichever format you prefer
    image_bytes.seek(0)  # Reset the stream position


    upload_result = cloudinary.uploader.upload(image_bytes.getvalue(), folder="Mythesis_images")
    public_id = upload_result["public_id"].replace("/", ":")

    video_url = cloudinary.CloudinaryVideo("bgvideo").video(transformation=[
    {'overlay': "black_bg_9_16"},
    {'flags': "layer_apply",'width': 2200, 'crop': "fit"},
    {'overlay': public_id},
    {'flags': "layer_apply",'width': 1920, 'crop': "fit"},
    {'overlay': "audio:reelaudio"},
    {'flags': "layer_apply"},
    {'width': 500, 'crop': "scale"},
    {'overlay': {'font_family': "arial", 'font_size': 18, 'font_weight': "bold", 'text': "Style", 'text': headline},'color': "white",'background':"black", 'width': 400, 'crop': "fit"},  
    {'flags': "layer_apply", 'gravity': "north", 'y': 500},
    {'overlay': {'font_family': "arial", 'font_size': 20, 'font_weight': "bold", 'text': "Style", 'text': "    autoFeed_tech"},'color': "black",'background':"skyblue", 'radius': 20, 'x': 20,'y': 20, 'width': 400, 'crop': "fit"},  # Added color: "white"
    {'flags': "layer_apply", 'gravity': "north", 'y': 110},
    {'overlay': {'font_family': "arial", 'font_size': 12, 'font_weight': "bold", 'text': "Style", 'text': "This page is totally handled by ai,which provides trending tech news faster than human!- Follow us Now"},'color': "white",'width': 380, 'crop': "fit"},  # Added color: "white"
    {'flags': "layer_apply", 'gravity': "north", 'y': 160}

    ])

    match = re.search(r'/webm"><source src="(.*\.mp4)"', str(video_url))
    mp4_url = match.group(1)
    print(mp4_url)


    # 🔹 6. Upload & Publish the Instagram Reel
    upload_url = f"https://graph.facebook.com/v18.0/{INSTAGRAM_ACCOUNT_ID}/media"
    payload = {
        "video_url": mp4_url,
        "caption": caption_text,
        "media_type": "REELS",
        "access_token": ACCESS_TOKEN
    }

    response = requests.post(upload_url, data=payload)
    response_data = response.json()
    print(response_data)

    media_id = response_data.get("id")
    print(media_id)

    if media_id:
        print("⏳ Waiting for Instagram to process the video...")
        time.sleep(40)

        publish_url = f"https://graph.facebook.com/v18.0/{INSTAGRAM_ACCOUNT_ID}/media_publish"
        publish_payload = {
            "creation_id": media_id,
            "access_token": ACCESS_TOKEN
        }
        publish_response = requests.post(publish_url, data=publish_payload)
        print("✅ Reel Uploaded Successfully!", publish_response.json())
    else:
        print("❌ Error: Failed to upload the video.")

post_reel()
