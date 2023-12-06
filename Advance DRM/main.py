from flask import Flask, render_template, request,jsonify,url_for,redirect
import sqlite3
from io import BytesIO
from base64 import b64encode
import watermark
import getHash
import userDataStorage
from PIL import Image

app = Flask(__name__)
DATABASE = 'user_database.db'
connect = sqlite3.connect(DATABASE,check_same_thread=False)

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
        if img1 and img2:
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

@app.route('/uploadMarksheet', methods=['GET', 'POST'])
def upload_marksheet():
    if request.method == 'POST':
        user_id = request.form.get('userId')
        user_name = request.form.get('userName')
        document = request.files['document']
        document.filename = user_id + '.png'
        document.save('Advance DRM/storedMarksheet/'+document.filename)
        document_hash = getHash.calculate_sha256('Advance DRM/storedMarksheet/'+document.filename)
        userDataStorage.sc.setUserDetails(user_id,user_name,document_hash,'Advance DRM/storedMarksheet/'+document.filename,1231244).transact()
    return render_template('upload-marksheet.html')

@app.route('/getMarksheet', methods=['GET', 'POST'])
def getMarksheet():
    if request.method == 'POST':
        userId = request.form.get('scholarNumber')
        document_path = userDataStorage.sc.getDocPath(userId).call()
        user_name = userDataStorage.sc.getUserName(userId).call()
        valid_user = userDataStorage.sc.isUserValid(userId).call()
        document_image = Image.open(document_path)
        buffered = BytesIO()
        document_image.save(buffered, format="JPEG")
        img_str = "data:image/jpeg;base64," + b64encode(buffered.getvalue()).decode()
        return jsonify({'document': img_str,'userName': user_name, 'validUser': valid_user})
    return render_template('get-marksheet.html')

@app.route('/validDocument', methods=['GET', 'POST'])
def validDocument():
    if request.method == 'POST':
        document = request.files['document']
        document.filename =  'temp.png'
        document.save('Advance DRM/storedMarksheet/'+document.filename)
        get_hash = getHash.calculate_sha256('Advance DRM/storedMarksheet/temp.png')
        validHash  = userDataStorage.sc.docHashExists(get_hash).call()
        return jsonify({'validDocument': validHash})
    return render_template('valid-Document.html')


if __name__ == '__main__':
    app.run(debug=True)
