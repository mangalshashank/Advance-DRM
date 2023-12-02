from flask import Flask, render_template, request,jsonify
import sqlite3


app = Flask(__name__)
DATABASE = 'user_database.db'
connect = sqlite3.connect(DATABASE,check_same_thread=False)


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # Get the values submitted in the form
        wallet_address = request.form['wallet_address']
        password = request.form['password']
        cursor = connect.cursor()
        cursor.execute('SELECT * FROM admin WHERE walletAddress = ? and password = ?', (wallet_address,password,))
        user = cursor.fetchone()
        if user is not None:
            return render_template('upload-marksheet.html')
        else:
            return render_template('invalid-address.html')
        
    return render_template('upload-marksheet.html')


if __name__ == '__main__':
    app.run(debug=True)
