from flask import Flask, request, jsonify, send_file
import requests
import io
from PIL import Image
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
from flask_cors import CORS




# ===================================================================================================================================
# ===================================================================================================================================


app = Flask(__name__)
CORS(app)  

# Set up Hugging Face API for image generation

API_URL = "https://api-inference.huggingface.co/models/Jovie/Midjourney"
headers = {"Authorization": "Bearer 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"}


# Set up the LLM

load_dotenv()
groq_api_key = os.environ['GROQ_API_KEY']
llm = ChatGroq(groq_api_key=groq_api_key, model_name="llama-3.1-8b-instant")




prompt = ChatPromptTemplate.from_template(
    """
    You are an expert AI art director. Create a detailed, photorealistic image description from the given theme.

    Theme: {input}

    Follow these key guidelines:

    1. Essential Elements:
    - Main subject with clear position and scale
    - Lighting and atmosphere
    - Color scheme
    - Camera angle and distance
    - Background context

    2. Quality Markers:
    - Include technical terms (4K, HDR, photorealistic)
    - Specify art style and rendering quality
    - Add mood and time of day
    - Mention key details and textures

    Rules:
    - Be specific and concrete
    - Focus on visual clarity
    - Keep descriptions between 30-50 words
    - Prioritize realism and detail

    Format: Create a single, flowing description incorporating all elements naturally.
    """
)


# ===================================================================================================================================
# ===================================================================================================================================


def query_image(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.content

@app.route('/generate_image', methods=['POST'])
def generate_image():
    try:
        data = request.json
        prompt_text = data.get('prompt')
        if not prompt_text:
            return jsonify({'error': 'No prompt provided'}), 400

        image_bytes = query_image({"inputs": prompt_text})
        return send_file(
            io.BytesIO(image_bytes),
            mimetype='image/jpeg',
            as_attachment=False
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    


# ===================================================================================================================================
# ===================================================================================================================================


if __name__ == '__main__':
    app.run(debug=True)