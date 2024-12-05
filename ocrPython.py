from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import pytesseract
import pandas as pd
from fuzzywuzzy import process
from PIL import Image
import numpy as np

# Konfigurasi Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Inisialisasi Flask
app = Flask(__name__)
CORS(app)  # Mengaktifkan CORS

# Memuat dataset
dataset_path = "datas.csv"  # Path ke dataset Anda
dataset = pd.read_csv(dataset_path)

# Fungsi OCR
def ocr_core(img):
    text = pytesseract.image_to_string(img, lang='eng', config='--psm 6 --oem 1')
    return text

# Preprocessing gambar
def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    denoised = cv2.medianBlur(gray, 3)
    binary = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    return binary

# Fungsi untuk mencari buku
def search_book(text, dataset):
    book_titles = dataset["title"].tolist()
    result = process.extractOne(text, book_titles)
    
    if result:
        matched_title = result[0]
        similarity = result[1]
        if similarity > 80:
            book_info = dataset[dataset["title"] == matched_title].iloc[0]
            return {
                "title": book_info["title"],
                "author": book_info["authors"],
                "description": book_info["description"],
            }
        elif similarity > 50:
            return {"suggestion": matched_title}
    
    return None

# Endpoint untuk proses OCR
@app.route('/process-ocr', methods=['POST'])
def process_ocr():
    try:
        if 'image' not in request.files:
            return jsonify({"error": "Tidak ada file gambar yang diunggah."}), 400

        file = request.files['image']

        if not file.content_type.startswith('image/'):
            return jsonify({"error": "File yang diunggah bukan gambar."}), 400

        img = Image.open(file.stream)
        img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        
        preprocessed = preprocess_image(img_cv)
        text = ocr_core(preprocessed)
        
        if not text.strip():
            return jsonify({"error": "Gambar tidak mengandung teks yang dapat dibaca."}), 400

        result = search_book(text, dataset)
        
        # Logging hasil pencarian untuk debugging
        print("Text hasil OCR:", text)
        print("Dataset Titles:", dataset["title"].tolist())
        print("Result:", result)

        if result:
            return jsonify(result), 200
        else:
            return jsonify({"error": "Buku tidak ditemukan.", "ocr_result": text}), 200
    except Exception as e:
        return jsonify({"error": f"Terjadi kesalahan: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
