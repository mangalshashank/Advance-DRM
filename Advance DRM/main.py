from flask import Flask, render_template, request,jsonify,url_for,redirect,send_file
import sqlite3
import numpy as np
import cv2
import watermarking
from werkzeug.utils import secure_filename
import os
from PIL import Image
from PIL import Image
from io import BytesIO
import numpy as np
from base64 import b64encode

app = Flask(__name__)
DATABASE = 'user_database.db'
connect = sqlite3.connect(DATABASE,check_same_thread=False)
temp_address = 0

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        wallet_address = request.form['wallet_address']
        password = request.form['password']
        cursor = connect.cursor()
        cursor.execute('SELECT * FROM admin WHERE walletAddress = ? and password = ?', (wallet_address,password,))
        user = cursor.fetchone()
        if user is not None:
            temp_address = wallet_address
            return redirect(url_for('upload_marksheet'))
        else:
            return render_template('invalid-address.html')
        
    return render_template('check-credential.html')


def adjust_brightness(img, factor):
    # Convert the image to RGB mode
    img = img.convert('RGB')

    # Adjust brightness using numpy
    img_array = np.array(img)
    adjusted_img_array = img_array * factor
    adjusted_img_array = np.clip(adjusted_img_array, 0, 255).astype(np.uint8)
    adjusted_img = Image.fromarray(adjusted_img_array)

    return adjusted_img

@app.route('/applyWatermark', methods=['GET', 'POST'])
def applyWatermark():
    return render_template('apply-watermark.html') 


@app.route('/adjust_brightness', methods=['POST'])
def adjust_brightness_route():
    factor = float(request.form['brightness_factor'])
    img_file = request.files['image']
    img = Image.open(img_file)
    adjusted_img = adjust_brightness(img, factor)
    
    # Convert the adjusted image to bytes for displaying in HTML
    buffered = BytesIO()
    adjusted_img.save(buffered, format="JPEG")
    img_str = "data:image/jpeg;base64," + b64encode(buffered.getvalue()).decode()
    
    return jsonify({'adjusted_img': img_str})


@app.route('/upload-marksheet', methods=['GET', 'POST'])
def upload_marksheet():
    return render_template('upload-marksheet.html')

if __name__ == '__main__':
    app.run(debug=True)
