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


def blend_images(img1, img2, factor):
    # Convert images to numpy arrays
    img1_array = np.array(img1)
    img2_array = np.array(img2)
    res = watermarking.apply_watermark(img1_array,img2_array,factor)
    # Perform image blending
    blended_img = Image.fromarray(res)
    # Ensure the blended image is in RGB mode
    blended_img = blended_img.convert('RGB')
    return blended_img

def extract_watermark(img1, img2, factor):
    # Convert images to numpy arrays
    img1_array = np.array(img1)
    img2_array = np.array(img2)
    res = watermarking.extract_watermark(img1_array,img2_array,factor)
    # Perform image blending
    blended_img = Image.fromarray(res)
    # Ensure the blended image is in RGB mode
    blended_img = blended_img.convert('RGB')
    return blended_img

@app.route('/blend_images', methods=['POST'])
def blend_images_route():
    factor = float(request.form['blend_factor'])
    img1_file = request.files['image1']
    img2_file = request.files['image2']
    img1 = Image.open(img1_file)
    img2 = Image.open(img2_file)
    blended_img = blend_images(img1, img2, factor)
    # Convert the blended image to bytes for displaying in HTML
    buffered = BytesIO()
    blended_img.save(buffered, format="JPEG")
    img_str = "data:image/jpeg;base64," + b64encode(buffered.getvalue()).decode()
    return jsonify({'blended_img': img_str})


@app.route('/applyWatermark', methods=['GET', 'POST'])
def applyWatermark():
    return render_template('apply-watermark.html') 

@app.route('/extractWatermark', methods=['GET', 'POST'])
def extractWatermark():
    if request.method == 'POST':
        factor = float(request.form['blend_factor'])
        img1_file = request.files['image1']
        img2_file = request.files['image2']
        img1 = Image.open(img1_file)
        img2 = Image.open(img2_file)
        blended_img = extract_watermark(img1,img2,factor)
        # Convert the blended image to bytes for displaying in HTML
        buffered = BytesIO()
        blended_img.save(buffered, format="JPEG")
        img_str = "data:image/jpeg;base64," + b64encode(buffered.getvalue()).decode()
        return jsonify({'blended_img': img_str})
    return render_template('extract-watermark.html')



@app.route('/upload-marksheet', methods=['GET', 'POST'])
def upload_marksheet():
    return render_template('upload-marksheet.html')

if __name__ == '__main__':
    app.run(debug=True)
