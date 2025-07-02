from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_pymongo import PyMongo
import os
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content, Attachment, FileContent, FileName, FileType, Disposition
from flask_cors import CORS
from dotenv import load_dotenv  # Make sure to install python-dotenv: pip install python-dotenv
from werkzeug.utils import secure_filename
import base64

load_dotenv()

app = Flask(__name__)


# MongoDB configuration
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
mongo = PyMongo(app)

# Allowed recipient emails for dropdown
ALLOWED_RECIPIENTS = [
    
    'lalji@perfectasianinteriors.com',
    'pankaj@perfectasianinteriors.com'
]

# Load environment variables
load_dotenv()
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')

# Allowed file extensions and max size (5MB)
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Homepage
@app.route('/')
def home():
    return render_template('home.html')

# Services Page
@app.route('/services')
def services():
    return render_template('services.html')

# Projects/Portfolio Page
@app.route('/projects')
def projects():
    projects = mongo.db.projects.find()
    return render_template('projects.html', projects=projects)

# About Us Page
@app.route('/about')
def about():
    return render_template('about.html')

# Testimonials Page
@app.route('/testimonials')
def testimonials():
    return render_template('testimonials.html')

# API: Get all testimonials (JSON)
@app.route('/get_testimonials')
def get_testimonials():
    testimonials = list(mongo.db.testimonials.find().sort('timestamp', -1))
    for t in testimonials:
        t['_id'] = str(t['_id'])
        t['timestamp'] = t.get('timestamp', '')
    return jsonify(testimonials)

# API: Submit a testimonial
@app.route('/submit_testimonial', methods=['POST'])
def submit_testimonial():
    data = request.get_json() if request.is_json else request.form
    name = data.get('name', '').strip()
    project = data.get('project', '').strip()
    feedback = data.get('feedback', '').strip()
    rating = int(data.get('rating', 0))
    if not name or not feedback or not (1 <= rating <= 5):
        return jsonify({'error': 'Invalid input'}), 400
    testimonial = {
        'name': name,
        'project': project,
        'feedback': feedback,
        'rating': rating,
        'timestamp': datetime.utcnow()
    }
    mongo.db.testimonials.insert_one(testimonial)
    return jsonify({'success': True}), 200

# Contact Page
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        subject = data.get('subject', '').strip()
        message = data.get('message', '').strip()
        if not name or not email or not subject or not message:
            return jsonify({'success': False, 'error': 'All fields are required.'}), 400
        if '@' not in email or '.' not in email:
            return jsonify({'success': False, 'error': 'Invalid email address.'}), 400
        # Send email via SendGrid to both recipients
        try:
            sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
            email_message = Mail(
                from_email='info@perfectasianinteriors.com',
                to_emails=ALLOWED_RECIPIENTS,
                subject=f'Contact Form: {subject}',
                html_content=f'<strong>Name:</strong> {name}<br><strong>Email:</strong> {email}<br><strong>Message:</strong> {message}'
            )
            sg.send(email_message)
            return jsonify({'success': True, 'message': 'Message sent successfully!'}), 200
        except Exception as e:
            return jsonify({'success': False, 'error': 'Failed to send message.'}), 500
    return render_template('contact.html')

# Request Quote Page
@app.route('/request-quote', methods=['GET', 'POST'])
def request_quote():
    if request.method == 'GET':
        return render_template('request_quote.html')
    # POST logic as before
    name = request.form.get('full_name', '').strip()
    service_type = request.form.get('service_type', '').strip()
    budget = request.form.get('budget', '').strip()
    contact_info = request.form.get('contact_info', '').strip()
    file = request.files.get('file_upload')
    errors = []
    # Validate required fields
    if not name:
        errors.append('Full Name is required.')
    if not service_type:
        errors.append('Service Type is required.')
    if not budget:
        errors.append('Budget is required.')
    if not contact_info:
        errors.append('Preferred Contact Info is required.')
    # Validate file
    file_data = None
    filename = None
    mimetype = None
    if file and file.filename:
        allowed_ext = {'pdf', 'jpg', 'jpeg', 'png'}
        ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        if ext not in allowed_ext:
            errors.append('Invalid file type. Only PDF, JPG, JPEG, PNG allowed.')
        else:
            file.seek(0, 2)
            file_length = file.tell()
            file.seek(0)
            if file_length > 5 * 1024 * 1024:
                errors.append('File size exceeds 5MB.')
            else:
                file_data = base64.b64encode(file.read()).decode()
                filename = secure_filename(file.filename)
                mimetype = file.mimetype
    if errors:
        return jsonify({'success': False, 'errors': errors}), 400
    # Send email via SendGrid
    try:
        sg = SendGridAPIClient(api_key=SENDGRID_API_KEY)
        from_email = Email('info@perfectasianinteriors.com')
        to_emails = ALLOWED_RECIPIENTS  # Send to both recipients
        subject = 'New Quote Request from Website'
        content = Content('text/html', f"""
            <h2>New Quote Request</h2>
            <p><b>Full Name:</b> {name}</p>
            <p><b>Service Type:</b> {service_type}</p>
            <p><b>Budget:</b> {budget}</p>
            <p><b>Preferred Contact Info:</b> {contact_info}</p>
        """)
        mail = Mail(from_email, to_emails, subject, content)
        # Attach file if present
        if file_data and filename and mimetype:
            attachment = Attachment()
            attachment.file_content = FileContent(file_data)
            attachment.file_type = FileType(mimetype)
            attachment.file_name = FileName(filename)
            attachment.disposition = Disposition('attachment')
            mail.attachment = attachment
        sg.send(mail)
        return jsonify({'success': True, 'message': 'Quote request sent successfully.'}), 200
    except Exception as e:
        print('SendGrid error:', e)
        return jsonify({'success': False, 'errors': ['Failed to send email. Please try again later.']}), 500

if __name__ == '__main__':
    app.run(debug=True) 
