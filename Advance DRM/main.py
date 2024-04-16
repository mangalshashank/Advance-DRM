from flask import Flask, render_template, request,jsonify, send_file,url_for,redirect
import sqlite3
from io import BytesIO
from base64 import b64encode
import watermark
import getHash
import userDataStorage
from PIL import Image
import os
import requests
import secret

app = Flask(__name__)
DATABASE = 'user_database.db'
connect = sqlite3.connect(DATABASE,check_same_thread=False)

@app.route('/')
def home():
    return render_template('home.html')

# LinkedIn API credentials
CLIENT_ID = secret.id
CLIENT_SECRET = secret.secret
REDIRECT_URI = 'http://localhost:5000/callback'  # This should match with your LinkedIn app settings

@app.route('/linkedInlogin', methods=['GET', 'POST'])
def linkedInlogin():
    params = {
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'scope': 'profile email openid',  # Adjust scope based on your requirements
    }
    auth_url = 'https://www.linkedin.com/oauth/v2/authorization?' + '&'.join([f'{key}={value}' for key, value in params.items()])
    return redirect(auth_url)

@app.route('/callback', methods=['GET', 'POST'])
def callback():
    code = request.args.get('code')
    if code:
        token_url = 'https://www.linkedin.com/oauth/v2/accessToken'
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }
        response = requests.post(token_url, data=data)
        access_token = response.json().get('access_token')
        if access_token:
            headers = { 'Authorization': f'Bearer {access_token}' }
            profile_url = 'https://api.linkedin.com/v2/userinfo'
            response = requests.get(profile_url, headers=headers)
            profile_data = response.json()
            return render_template('get-marksheet.html',user=profile_data)
        else:
            return "Failed to obtain access token"
    else:
        return "Error in callback"

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        wallet_address = request.form['wallet_address']
        password = request.form['password']
        cursor = connect.cursor()
        cursor.execute('SELECT * FROM admin WHERE walletAddress = ? and password = ?', (wallet_address,password,))
        user = cursor.fetchone()
        if user is not None:
            return redirect(url_for('upload_marksheet'))
        else:
            return render_template('invalid-address.html')
    return render_template('check-credential.html')

@app.route('/extendValidity', methods=['GET', 'POST'])
def extendValidity():
    if request.method == 'POST':
        wallet_address = request.form['wallet_address']
        password = request.form['password']
        cursor = connect.cursor()
        cursor.execute('SELECT * FROM admin WHERE walletAddress = ? and password = ?', (wallet_address,password,))
        user = cursor.fetchone()
        if user is not None:
            return redirect(url_for('extendedValidity'))
        else:
            return render_template('invalid-address.html')
    return render_template('check-credential-extended.html')

@app.route('/extendedValidity', methods=['GET', 'POST'])
def extendedValidity():
    if request.method == 'POST':
        user_id = request.form.get('userId')
        validity = request.form.get('validity')
        ok = False
        if validity is not None and int(validity) > 0:
            ok = True
            validity = int(validity)*86400
            userDataStorage.sc.extendDuration(user_id,validity).transact()
        return jsonify({'Success': ok})
    return render_template('extend-validity.html')

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
        userEmail = request.form.get('userEmail')
        validity = int(request.form.get('validity'))*86400
        document = request.files['document']
        document.filename = user_id + '.png'
        document.save('Advance DRM/storedMarksheet/'+document.filename)
        document_hash = getHash.calculate_sha256('Advance DRM/storedMarksheet/'+document.filename)
        cursor = connect.cursor()
        cursor.execute('INSERT INTO validemail (emailId, scholarNumber) VALUES (?,?)', (userEmail,user_id))
        connect.commit()
        userDataStorage.sc.setUserDetails(user_id,user_name,document_hash,'Advance DRM/storedMarksheet/'+document.filename,validity).transact()
        return jsonify({'success': True})
    return render_template('upload-marksheet.html')

@app.route('/getMarksheet', methods=['GET', 'POST'])
def getMarksheet():
    if request.method == 'POST':
        data = request.get_json()
        user_email = data['email']
        cursor = connect.cursor()
        cursor.execute('SELECT * FROM validemail WHERE emailId = ?', (user_email,))
        userId = str(cursor.fetchone()[1])
        if userId is None:
            return jsonify({'error': 'Invalid Email'})
        document_path = userDataStorage.sc.getDocPath(userId).call()
        user_name = userDataStorage.sc.getUserName(userId).call()
        valid_user = userDataStorage.sc.isUserValid(userId).call()
        document_image = Image.open(document_path)
        buffered = BytesIO()
        document_image.save(buffered, format="JPEG")
        img_str = "data:image/jpeg;base64," + b64encode(buffered.getvalue()).decode()
        return jsonify({'document': img_str,'userName': user_name,'validUser': valid_user})
    return render_template('get-marksheet.html')

@app.route('/validDocument', methods=['GET', 'POST'])
def validDocument():
    if request.method == 'POST':
        document = request.files['document']
        document.filename =  'temp.png'
        document.save('Advance DRM/storedMarksheet/'+document.filename)
        get_hash = getHash.calculate_sha256('Advance DRM/storedMarksheet/temp.png')
        os.remove('Advance DRM/storedMarksheet/temp.png')
        validHash  = userDataStorage.sc.docHashExists(get_hash).call()
        return jsonify({'validDocument': validHash})
    return render_template('valid-Document.html')

@app.route('/downloadMarksheet', methods= ['POST'])
def downloadMarksheet():
    if request.method == 'POST':
       # data = request.get_json()
       # user_email = data['email']
        user_email = request.form.get('email')
        cursor = connect.cursor()
        cursor.execute('SELECT * FROM validemail WHERE emailId = ?', (user_email,))
        userId = str(cursor.fetchone()[1])
        if userId is None:
            return jsonify({'error': 'Invalid Email'})
        document_path = userDataStorage.sc.getDocPath(userId).call()
        image = Image.open(document_path)
        buffer = BytesIO()
        image.save(buffer, format='PNG')
        buffer.seek(0)
            # Send the buffer as a file
        return send_file(
            buffer,
            mimetype='image/png',
            download_name='processed_image.png',
            as_attachment=True
        )
    return render_template('get-marksheet.html')
    

if __name__ == '__main__':
    app.run(debug=True)
