from flask import Flask, render_template, request,jsonify,url_for,redirect
import sqlite3
from io import BytesIO
from base64 import b64encode
import watermark

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

@app.route('/applyWatermark', methods=['GET', 'POST'])
def applyWatermark():
    if request.method == 'POST':
        img1 = request.files['coverImage']
        img2 = request.files['watermarkImage']
        blended_img = watermark.apply_watermark(img1,img2)
        buffered = BytesIO()
        blended_img.save(buffered, format="JPEG")
        img_str = "data:image/jpeg;base64," + b64encode(buffered.getvalue()).decode()
        return jsonify({'watermarked_img': img_str})
    return render_template('apply-watermark.html') 

@app.route('/extractWatermark', methods=['GET', 'POST'])
def extractWatermark():
    if request.method == 'POST':
        watermarkedImage = request.files['watermarkedImage']
        blended_img = watermark.recover_watermark(watermarkedImage)
        buffered = BytesIO()
        blended_img.save(buffered, format="JPEG")
        img_str = "data:image/jpeg;base64," + b64encode(buffered.getvalue()).decode()
        return jsonify({'watermark': img_str})
    return render_template('extract-watermark.html')

@app.route('/upload-marksheet', methods=['GET', 'POST'])
def upload_marksheet():
    return render_template('upload-marksheet.html')

if __name__ == '__main__':
    app.run(debug=True)
