from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pytesseract
from PIL import Image
import io
from deep_translator import GoogleTranslator
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
load_dotenv()
from langchain_core.messages import HumanMessage,SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
parser = StrOutputParser()

translated_text_en = None

groq_api_key = os.getenv("GROQ_API_KEY")
groq_api_key

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        
        img_bytes = file.read()
        image = Image.open(io.BytesIO(img_bytes))

        
        text = pytesseract.image_to_string(image)
        global translated_text_en
        
        translator_en = GoogleTranslator(source='auto', target='en')
        translator_hi = GoogleTranslator(source='auto', target='hi')
        translator_mr = GoogleTranslator(source='auto', target='mr')

        translated_text_en = translator_en.translate(text)  
        translated_text_hi = translator_hi.translate(text)  
        translated_text_mr = translator_mr.translate(text)  

        
        return jsonify({
            "OCR Result": text,
            "Translated to English": translated_text_en,
            "Translated to Hindi": translated_text_hi,
            "Translated to Marathi": translated_text_mr
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/chatbot', methods=['POST'])
def chatbot():
    try:
        
        user_input = request.json.get("message")
        if not user_input:
            return jsonify({"error": "No message provided"}), 400

        
        model = ChatGroq(model="Gemma2-9b-It", groq_api_key=groq_api_key)

       
        global translated_text_en

        
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"The following text was extracted and translated: {translated_text_en}. You can interact based on this text."),
            ("user", "{text}")
        ])

        
        parser = StrOutputParser()

        
        chain = prompt | model | parser

       
        response = chain.invoke({"text": user_input})

        
        return jsonify({"response": response})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
