from flask import Flask, render_template, request, send_file, redirect, url_for, flash
from fpdf import FPDF
from PIL import Image, ImageEnhance, ImageFilter
import io
import os
import textwrap
from datetime import datetime
from werkzeug.utils import secure_filename
from werkzeug.middleware.proxy_fix import ProxyFix
from chatbot import get_response, load_intents, expecting_pdf_text

import sys
sys.path.append('.')  # in case local modules aren't loading

app = Flask(__name__)
app.secret_key = 'secret'

UPLOAD_FOLDER = '/tmp/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

chat_history = []
intents = load_intents()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    global expecting_pdf_text
    user_input = request.form['user_input'].strip()
    bot_response = get_response(user_input, intents)

    if "PDF" in bot_response and "created successfully" in bot_response:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", size=12)
        wrapped_lines = textwrap.wrap(user_input, width=90)
        for line in wrapped_lines:
            pdf.cell(0, 10, txt=line, new_x="LMARGIN", new_y="NEXT")

        pdf_bytes = io.BytesIO()
        pdf.output(pdf_bytes)
        pdf_bytes.seek(0)

        filename = f"user_note_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        return send_file(pdf_bytes, mimetype='application/pdf', as_attachment=True, download_name=filename)

    chat_history.append(f"User: {user_input}")
    chat_history.append(f"Chotu: {bot_response}")
    return render_template("index.html", bot_response=bot_response)

@app.route('/upload_image', methods=['POST'])
def upload_image():
    file = request.files['file']
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        flash("Image uploaded successfully.")
        return redirect(url_for('edit_image', filename=filename))
    flash("No file uploaded.")
    return redirect(url_for('index'))

@app.route('/uploads/<filename>')
def serve_uploaded_file(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return send_file(filepath)

@app.route('/edit/<filename>')
def edit_image(filename):
    image_url = url_for('serve_uploaded_file', filename=filename)
    return render_template('edit_image.html', filename=filename, image_url=image_url)

@app.route('/apply_filters', methods=['POST'])
def apply_filters():
    filename = request.form['filename']
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(filepath):
        flash("File not found.")
        return redirect(url_for('index'))

    image = Image.open(filepath)

    contrast = float(request.form.get('contrast', 1.0))
    brightness = float(request.form.get('brightness', 1.0))
    grayscale = 'grayscale' in request.form
    blur_radius = float(request.form.get('blur', 0.0))
    rotate = int(request.form.get('rotate', 0))

    if contrast != 1.0:
        image = ImageEnhance.Contrast(image).enhance(contrast)
    if brightness != 1.0:
        image = ImageEnhance.Brightness(image).enhance(brightness)
    if grayscale:
        image = image.convert("L").convert("RGB")
    if blur_radius > 0:
        image = image.filter(ImageFilter.GaussianBlur(blur_radius))
    if rotate != 0:
        image = image.rotate(-rotate, expand=True)

    img_bytes = io.BytesIO()
    image.save(img_bytes, format='PNG')
    img_bytes.seek(0)

    edited_filename = f"edited_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
    return send_file(
        img_bytes,
        mimetype='image/png',
        as_attachment=True,
        download_name=edited_filename
    )

app.wsgi_app = ProxyFix(app.wsgi_app)

app = app  # for Vercel to detect the WSGI app