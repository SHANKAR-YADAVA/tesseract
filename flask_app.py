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
        # Read the image file into memory
        img_bytes = file.read()
        image = Image.open(io.BytesIO(img_bytes))

        # Perform OCR using Tesseract to extract text
        text = pytesseract.image_to_string(image)

        # Auto-detect the source language and translate to Hindi, Marathi, and English
        translator_en = GoogleTranslator(source='auto', target='en')
        translator_hi = GoogleTranslator(source='auto', target='hi')
        translator_mr = GoogleTranslator(source='auto', target='mr')

        translated_text_en = translator_en.translate(text)  # Translate to English
        translated_text_hi = translator_hi.translate(text)  # Translate to Hindi
        translated_text_mr = translator_mr.translate(text)  # Translate to Marathi

        # Return the original OCR result and translations
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
    user_input = request.json.get("message")
    # Here you would implement your LangChain logic to get the response based on user_input
    # For demonstration purposes, let's return a simple echo response.
    response = f"You said: {user_input}"  # Replace this with your LangChain response
    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(debug=True)
