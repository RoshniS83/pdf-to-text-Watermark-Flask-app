# # Store this code in 'app.py' file
#
# from flask import Flask, render_template, request, redirect, url_for, session, flash
# from flask_mysqldb import MySQL
# import MySQLdb.cursors
# import re
# import os
# from werkzeug.utils import secure_filename
# import PyPDF2
# from PIL import Image, ImageDraw
# from flask import send_from_directory
# import shutil
#
# app = Flask(__name__)
#
# app.secret_key = 'your secret key'
#
# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = 'Roshni'
# app.config['MYSQL_DB'] = 'pdfprojectuser'
# app.config['UPLOAD_FOLDER'] = 'watermarkedPDF/'
#
# mysql = MySQL(app)
#
#
# def convert_pdf_to_text(pdf_path):
#     text = ""
#     with open(pdf_path, 'rb') as pdf_file:
#         reader = PyPDF2.PdfFileReader(pdf_file)
#         for page in range(reader.getNumPages()):
#             text += reader.getPage(page).extract_text()
#     return text
#
# def apply_watermark(pdf_path, watermark_path):
#     # Open PDF and watermark
#     pdf_image = Image.open(pdf_path)  # Assuming the PDF is converted to an image, or use pdf2image
#     watermark = Image.open(watermark_path).convert("RGBA")
#
#     # Combine images
#     pdf_image.paste(watermark, (0, 0), watermark)
#     watermarked_pdf_path = pdf_path.replace('.pdf', '_watermarked.pdf')
#     pdf_image.save(watermarked_pdf_path)
#
#     return watermarked_pdf_path
#
# @app.route('/')
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     msg = ''
#     if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
#         username = request.form['username']
#         password = request.form['password']
#         cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#         cursor.execute('SELECT * FROM accounts WHERE username = % s AND password = % s', (username, password,))
#         account = cursor.fetchone()
#         if account:
#             session['loggedin'] = True
#             session['id'] = account['id']
#             session['username'] = account['username']
#             msg = 'Logged in successfully !'
#             return render_template('index.html', msg=msg)
#         else:
#             msg = 'Incorrect username / password !'
#     return render_template('login.html', msg=msg)
#
# @app.route('/index')
# def index():
#     if 'loggedin' in session:
#         return render_template('index.html')
#     return redirect(url_for('login'))
#
# @app.route('/logout')
# def logout():
#     session.pop('loggedin', None)
#     session.pop('id', None)
#     session.pop('username', None)
#     return redirect(url_for('login'))
#
#
# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     msg = ''
#     if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
#         username = request.form['username']
#         password = request.form['password']
#         email = request.form['email']
#         cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#         cursor.execute('SELECT * FROM accounts WHERE username = % s', (username,))
#         account = cursor.fetchone()
#         if account:
#             msg = 'Account already exists !'
#         elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
#             msg = 'Invalid email address !'
#         elif not re.match(r'[A-Za-z0-9]+', username):
#             msg = 'Username must contain only characters and numbers !'
#         elif not username or not password or not email:
#             msg = 'Please fill out the form !'
#         else:
#             cursor.execute('INSERT INTO accounts VALUES (NULL, % s, % s, % s)', (username, password, email,))
#             mysql.connection.commit()
#             msg = 'You have successfully registered !'
#     elif request.method == 'POST':
#         msg = 'Please fill out the form !'
#     return render_template('register.html', msg=msg)
#
#
# @app.route('/process_files', methods=['POST'])
# def process_files():
#     if 'loggedin' not in session:
#         return redirect(url_for('login'))
#
#     if 'pdf' not in request.files or 'watermark' not in request.files:
#         flash('No file part')
#         return redirect(url_for('index'))
#
#     pdf = request.files['pdf']
#     watermark = request.files['watermark']
#
#     if pdf.filename == '' or watermark.filename == '':
#         flash('No selected file')
#         return redirect(url_for('index'))
#
#     pdf_filename = secure_filename(pdf.filename)
#     watermark_filename = secure_filename(watermark.filename)
#
#     # Save the files to the upload folder
#     pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename)
#     watermark_path = os.path.join(app.config['UPLOAD_FOLDER'], watermark_filename)
#
#     pdf.save(pdf_path)
#     watermark.save(watermark_path)
#
#     # Apply watermark and save to the static folder for display
#     watermarked_pdf_path = apply_watermark(pdf_path, watermark_path)
#     watermarked_pdf_filename = os.path.basename(watermarked_pdf_path)
#     watermarked_pdf_url = os.path.join('watermarkedPDF', watermarked_pdf_filename)
#
#     # Move the watermarked PDF to the static folder for access
#     watermarked_static_path = os.path.join('static', watermarked_pdf_url)
#     # os.rename(watermarked_pdf_path, watermarked_static_path)
#     shutil.move(watermarked_pdf_path, watermarked_static_path)
#     return render_template('index.html', watermarked_pdf_url=watermarked_pdf_url)
#     # flash('Files uploaded and processed successfully')
#     # return redirect(url_for('index'))
#
# @app.route('/download/<filename>')
# def download_pdf(filename):
#     return send_from_directory('static/watermarkedPDF', filename, as_attachment=True)
#
# if __name__ == '__main__':
#     app.run(debug=True)
import random

from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from flask_mysqldb import MySQL
from flask_mail import Mail,Message
import MySQLdb.cursors
import re
import os
from datetime import datetime, timedelta
import random
from werkzeug.utils import secure_filename
import PyPDF2
import fitz  # PyMuPDF
import numpy as np
import cv2
import shutil
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import math

app = Flask(__name__)
app.secret_key = 'your secret key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Roshni'
app.config['MYSQL_DB'] = 'pdfprojectuser'
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'roshni.sundrani83@gmail.com'
app.config['MAIL_PASSWORD'] = 'wutu jttw tlyn iowo'
app.config['MAIL_DEFAULT_SENDER']='roshni.sundrani83@gmail.com'

mail = Mail(app)
mysql = MySQL(app)

# Example route to test email sending
@app.route('/test-email')
def test_email():
    try:
        msg = Message('Test Email', recipients=['roshni.sundrani83@gmail.com'])
        msg.body = 'This is a test email from Flask.'
        mail.send(msg)
        return 'Test email sent!'
    except Exception as e:
        return f'Error sending email: {e}'
# class Accounts(mysql.Model):
#     id = mysql.Column(mysql.Integer, primary_key=True)
#     email = mysql.Column(mysql.String(150), unique=True, nullable=False)
#     password = mysql.Column(mysql.String(150), nullable=False)
#     otp = mysql.Column(mysql.String(6))
#     otp_created_at = mysql.Column(mysql.DateTime)

@app.route('/forgot-password')
def forgot_password():
    return render_template('forgot_password.html')


@app.route('/sendOTP', methods=['POST'])
def send_otp_email():
    email = request.form.get('email')

    if not email:
        flash('Email is required.')
        return redirect(url_for('forgot_password'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        cursor.execute('SELECT * FROM accounts WHERE email = %s', (email,))
        accounts = cursor.fetchone()

        if accounts:
            otp = str(random.randint(100000, 999999))
            otp_created_at = datetime.utcnow()
            print(f'Generated OTP : {otp}  and  {otp_created_at}')

            cursor.execute('UPDATE accounts SET otp = %s, otp_created_at = %s WHERE id = %s',
                           (otp, otp_created_at, accounts['id']))
            mysql.connection.commit()

            expiration_time = otp_created_at + timedelta(minutes=1)
            expiration_time_str = expiration_time.strftime('%Y-%m-%d %H:%M:%S UTC')

            msg = Message('Your OTP code',
                          recipients=[accounts['email']],
                          body=f'Your OTP code is {otp}. It is valid until {expiration_time_str}')

            mail.send(msg)
            print('OTP mail sent')
            flash('OTP has been sent to your email. It is valid for 1 minute.','success')
        else:
            flash('Email not found.')
    except Exception as e:
        print(f'Error occurred: {e}')
        flash('An error occurred while sending the OTP.', 'error')

    return redirect(url_for('forgot_password'))


@app.route('/reset-password', methods=['POST'])
def reset_password():
    email = request.form.get('email')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM accounts WHERE email = %s', (email,))
    user = cursor.fetchone()

    if user:
        print('User found, calling send_otp_email')
        # Here, you would redirect to the /sendOTP route instead of directly calling the function
        return redirect(url_for('send_otp_email'))
    else:
        flash('Email not found.')

    return redirect(url_for('forgot_password'))


@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    otp = request.form.get('otp')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM accounts WHERE otp = %s', (otp,))
    user = cursor.fetchone()

    if user and datetime.utcnow() - user['otp_created_at'] < timedelta(minutes=1):
        # OTP is valid, redirect to password reset form
        return redirect(url_for('set_new_password', email=user['email']))
    else:
        flash('Invalid or expired OTP.')
        return redirect(url_for('forgot_password'))

@app.route('/set-new-password', methods=['GET', 'POST'])
def set_new_password():
    email = request.args.get('email')
    if request.method == 'POST':
        # email = request.form.get('email')
        new_password = request.form.get('newPassword')
        confirm_password = request.form.get('confirmPassword')

        if new_password == confirm_password:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('UPDATE accounts SET password = %s, otp = NULL WHERE email = %s',
                           (new_password, email))
            mysql.connection.commit()  # Commit the changes to the database
            flash('Password has been reset successfully.')
            return redirect(url_for('login'))
        else:
            flash('Passwords do not match.')
            return redirect(url_for('set_new_password', email=email))

    email = request.args.get('email')
    return render_template('set_new_password.html', email=email)

def create_text_watermark(text, output_path):
    c = canvas.Canvas(output_path, pagesize=letter)
    c.setFont("Helvetica", 40)
    c.setFillColorRGB(0.6, 0.6, 0.6, alpha=0.3)  # Set the color and transparency
    width, height = letter
    # Calculate the angle and the positioning
    angle = 45  # Slanting angle in degrees
    radian_angle = math.radians(angle)
    # Position for the text to be centered after rotation
    text_width = c.stringWidth(text, "Helvetica", 40)
    x = (width - text_width * math.cos(radian_angle)) / 2
    y = height / 2
    # Rotate and draw the text
    c.translate(width / 2, height / 2)  # Move origin to center
    c.rotate(angle)
    c.drawString(-text_width / 2, 0, text)  # Draw text centered on the new origin
    # c.drawString(width / 4, height / 2, text)
    c.save()

# Function to create text watermark
# def create_text_watermark(text, output_path):
#     c = canvas.Canvas(output_path, pagesize=letter)
#     c.setFont("Helvetica", 40)
#     c.setFillColorRGB(0.9, 0.9, 0.9)  # Set the color (alpha is not supported directly by ReportLab)
#
#     width, height = letter
#
#     # Calculate the angle and the positioning
#     angle = 45  # Slanting angle in degrees
#     radian_angle = math.radians(angle)
#
#     # Position for the text to be centered after rotation
#     text_width = c.stringWidth(text, "Helvetica", 40)
#     x = (width - text_width * math.cos(radian_angle)) / 2
#     y = height / 2
#
#     # Rotate and draw the text
#     c.translate(width / 2, height / 2)  # Move origin to center
#     c.rotate(angle)
#     c.drawString(-text_width / 2, 0, text)  # Draw text centered on the new origin
#
#     c.save()


def add_text_watermark(input_pdf, output_pdf, watermark_pdf):
    reader = PyPDF2.PdfReader(input_pdf)
    writer = PyPDF2.PdfWriter()

    watermark = PyPDF2.PdfReader(watermark_pdf).pages[0]

    for page in reader.pages:
        page.merge_page(watermark)
        writer.add_page(page)

    with open(output_pdf, "wb") as output_file:
        writer.write(output_file)


def convert_pdf_to_text(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfFileReader(pdf_file)
        for page in range(reader.getNumPages()):
            text += reader.getPage(page).extract_text()
    return text


def create_transparent_image(image_path, alpha=0.1):
    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    if image.shape[2] == 3:
        alpha_channel = np.ones((image.shape[0], image.shape[1]), dtype=image.dtype) * 255
        image = np.dstack((image, alpha_channel))

    image[:, :, 3] = (image[:, :, 3] * alpha).astype(image.dtype)
    transparent_image_path = image_path.replace('.jpg', '_transparent.png')
    cv2.imwrite(transparent_image_path, image)
    return transparent_image_path


def add_watermark_vector(input_pdf, output_pdf, watermark_img):
    pdf = fitz.open(input_pdf)
    for page_num in range(len(pdf)):
        page = pdf[page_num]
        rect = page.rect
        page.insert_image(rect, filename=watermark_img, overlay=True, keep_proportion=True)
    pdf.save(output_pdf)
    pdf.close()


# @app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            flash('Logged in successfully!', 'success')
            return render_template('index.html', msg=msg)
        else:
            flash('Incorrect username / password!', 'error')
    return render_template('register.html', msg=msg)


@app.route('/index')
def index():
    if 'loggedin' in session:
        return render_template('index.html')
    return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    flash('You have been successfully logged Out!','info' )
    return redirect(url_for('login'))




@app.route('/')
@app.route('/register', methods=['POST','GET'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        if account:
            flash('Account already exists!', 'error')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Invalid email address!', 'error')
        elif not re.match(r'[A-Za-z0-9]+', username):
            flash('Username must contain only characters and numbers!', 'error')
        elif not username or not password or not email:
            flash('Please fill out the form!', 'error')
        else:
            cursor.execute('INSERT INTO accounts (username, password, email) VALUES (%s, %s, %s)',
                           (username, password, email))
            mysql.connection.commit()
            flash('You have successfully registered!', 'success')
            return redirect(url_for('register'))
    elif request.method == 'POST':
        flash('Please fill out the form!')
    return render_template('register.html', msg=msg)


@app.route('/process_files', methods=['POST'])
def process_files():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    if 'pdfFile' not in request.files:
        flash('No PDF file provided')
        return redirect(url_for('index'))

    pdf_file =request.files['pdfFile']
    watermark_type = request.form['watermarkType']
    watermarked_pdf_url = None
    if watermark_type == 'text':
        text = request.form.get('textWatermark')
        if not text :
            flash('No watermark text provided !! please write some text for watermark')
            return redirect(url_for('index'))
        filename = process_text_watermark(pdf_file, text)
    elif watermark_type =='image':
        image= request.files.get('imageWatermark')
        filename = process_image_watermark(pdf_file, image)
    else:
        filename = process_pdf_without_watermark(pdf_file)

    # output_path = os.path.join('static','watermarkedPDF', filename)
    # if os.path.exists(output_path):
    #     watermarked_pdf_url = output_path
    return redirect(url_for('download_pdf', filename = filename))
    # return render_template('index.html', watermarked_pdf_url=watermarked_pdf_url)

def process_text_watermark(pdf_file, watermark_text):
    pdf_filename = secure_filename(pdf_file.filename)
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename)
    pdf_file.save(pdf_path)
    # Create the watermark PDF with the text
    watermark_pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], 'text_watermark.pdf')
    create_text_watermark(watermark_text, watermark_pdf_path)
    # Apply the text watermark to the PDF
    watermarked_pdf_path = pdf_path.replace('.pdf', '_text_watermarked.pdf')
    add_text_watermark(pdf_path, watermarked_pdf_path, watermark_pdf_path)
    watermarked_pdf_filename = os.path.basename(watermarked_pdf_path)
    watermarked_pdf_url = watermarked_pdf_filename  # Only filename for URL
    # Ensure the destination directory exists
    watermarked_static_dir = os.path.join('static', 'watermarkedPDF')
    os.makedirs(watermarked_static_dir, exist_ok=True)
    # Move the watermarked PDF to the static folder for access
    watermarked_static_path = os.path.join(watermarked_static_dir, watermarked_pdf_filename)
    shutil.move(watermarked_pdf_path, watermarked_static_path)
    return os.path.basename(watermarked_static_path)
    # return render_template('index.html', watermarked_pdf_url=watermarked_pdf_url)
# @app.route('/process_files', methods=['POST'])
def process_image_watermark(pdf_file, image):
    pdf_filename = secure_filename(pdf_file.filename)
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename)
    pdf_file.save(pdf_path)

    watermark_filename = secure_filename(image.filename)
    watermark_path = os.path.join(app.config['UPLOAD_FOLDER'], watermark_filename)
    image.save(watermark_path)

    # Create a transparent watermark image
    transparent_watermark_path = create_transparent_image(watermark_path)
    watermarked_pdf_path = pdf_path.replace('.pdf', '_image_watermarked.pdf')

    add_watermark_vector(pdf_path, watermarked_pdf_path, transparent_watermark_path)

    # Ensure the destination directory exists
    watermarked_static_dir = os.path.join('static', 'watermarkedPDF')
    os.makedirs(watermarked_static_dir, exist_ok=True)

    # Move the watermarked PDF to the static folder for access
    watermarked_static_path = os.path.join(watermarked_static_dir, os.path.basename(watermarked_pdf_path))
    shutil.move(watermarked_pdf_path, watermarked_static_path)

    return os.path.basename(watermarked_static_path)

    # pdf_filename = secure_filename(pdf_file.filename)
    # watermark_filename = secure_filename(watermark.filename)
    # pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename)
    # watermark_path = os.path.join(app.config['UPLOAD_FOLDER'], watermark_filename)
    # pdf_file.save(pdf_path)
    # watermark.save(watermark_path)
    # transparent_watermark_path = create_transparent_image(watermark)
    # watermarked_pdf_path = pdf_path.replace('.pdf', '_watermarked.pdf')
    # add_watermark_vector(pdf_path, watermarked_pdf_path, transparent_watermark_path)
    # watermarked_pdf_filename = os.path.basename(watermarked_pdf_path)
    # watermarked_pdf_url = watermarked_pdf_filename  # Only filename for URL
    # # Ensure the destination directory exists
    # watermarked_static_dir = os.path.join('static', 'watermarkedPDF')
    # os.makedirs(watermarked_static_dir, exist_ok=True)
    # # Move the watermarked PDF to the static folder for access
    # watermarked_static_path = os.path.join(watermarked_static_dir, watermarked_pdf_url)
    # shutil.move(watermarked_pdf_path, watermarked_static_path)
    # return os.path.basename(watermarked_static_path)
    # # return render_template('index.html', watermarked_pdf_url=watermarked_pdf_url)

def process_pdf_without_watermark(pdf_file):
    pdf_filename = secure_filename(pdf_file.filename)
    pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename)
    pdf_file.save(pdf_path)

@app.route('/download/<filename>')
def download_pdf(filename):
    return send_from_directory('static/watermarkedPDF', filename, as_attachment=True)

# @app.route('/logout')
# def logout():
#     #REmove user from session
#     session.pop('user_id', None)
#     return redirect((url_for('login')))


if __name__ == '__main__':
    app.run(debug=True)
