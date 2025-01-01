from flask import Flask, request, jsonify, send_file
import requests
import io
from PIL import Image
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
from flask_cors import CORS


#====================================================================================================================================
#====================================================================================================================================

load_dotenv()
groq_api_key = os.environ['GROQ_API_KEY']

app = Flask(__name__)
CORS(app) 

# Set up Hugging Face API for image generation
API_URL = "https://api-inference.huggingface.co/models/Jovie/Midjourney"
headers = {"Authorization": "Bearer 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"}


#====================================================================================================================================
#====================================================================================================================================

# Set up the prompt template
prompt = ChatPromptTemplate.from_template(
    """
    You are an AI creative assistant that generates vivid and descriptive artwork prompts based solely on a given theme.
    Your goal is to craft imaginative descriptions that will inspire the creation of dynamic artwork.

    Instructions:
    Theme: Use the provided theme as the primary focus for your description.
    Imagery: Create a detailed scene that embodies the essence of the theme.
    Descriptive Language: Utilize rich and evocative language to paint a picture in the reader's mind.
    Creative Freedom: Feel free to add imaginative elements that enhance the theme and make it more realistics.

    Rules:
    1) you need to genetate prompt which makes image in clear way.


    {input}.
    """
)


#====================================================================================================================================
#====================================================================================================================================


# Set up the LLM
llm = ChatGroq(groq_api_key=groq_api_key, model_name="llama-3.1-8b-instant")

def query_image(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.content

def generate_text_response(topic):
    llm_chain = LLMChain(
        llm=llm,
        prompt=prompt,
        verbose=True
    )
    response = llm_chain.invoke({"input": topic})
    print("Redsssss---->  ",response['text'])

    return response['text']



@app.route('/generate_text', methods=['POST'])
def generate_text():
    try:
        data = request.json
        topic = data.get('topic')
        if not topic:
            return jsonify({'error': 'No topic provided'}), 400

        text_description = generate_text_response(topic)
        return jsonify({'description': text_description})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    


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
    

#====================================================================================================================================
#====================================================================================================================================



if __name__ == '__main__':
    app.run(debug=True)
