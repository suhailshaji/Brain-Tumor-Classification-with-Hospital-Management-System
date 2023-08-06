from flask import Blueprint,render_template,request,redirect,flash,session,url_for
from hms.database import *
from datetime import datetime
import random
import string
from flask_mail import Message
from flask_mail import Mail, Message
from flask import Blueprint, current_app


public = Blueprint('public',__name__)

# Function to generate a random ID
def generate_patient_id():
    prefix = "MRA"
    random_number = ''.join(random.choices(string.digits, k=5))
    return prefix + random_number


@public.route('/')
def index():
    return render_template('home.html')
    


@public.route('/login', methods=['POST', 'GET'])
def login():
    if 'submit' in request.form:
        username = request.form['username']
        password = request.form['password']

        q = "SELECT * FROM login WHERE username='%s' AND password='%s'" % (username, password)
        res = select(q)

        if res:
            session['login_id'] = res[0]['login_id']
            login_type = res[0]['user_type']
            print("Login Type",login_type)
            if login_type == "admin":
                flash('Welcome, Admin!')
                return redirect(url_for("admin.index_admin"))

            elif login_type == "patient":
                flash('Welcome, Patient!')
                return redirect(url_for("patient.patient_home"))

            elif login_type == "receptionist":
                flash('Welcome, Receptionist!')
                return redirect(url_for("receptionist.receptionist_home"))

            elif login_type == "doctor":
                flash('Welcome, Doctor!')
                return redirect(url_for("doctor.doctor_home"))

            
            elif login_type == "radiologist":
                flash('Welcome, Radiology Department!')
                return redirect(url_for("radiologist.radiologist_home"))

        else:
            flash('Invalid username or password!')

    return render_template('login.html')

@public.route('/register')
def register():

    return render_template('register_patient.html')   
    


@public.route('/register_patient',methods=['POST'])
def register_patinet():
    # Retrieve form data
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    password = request.form['password']
    date_of_birth = datetime.strptime(request.form['date_of_birth'], '%d-%m-%Y').strftime('%Y-%m-%d')
    gender = request.form['gender']
    address = request.form['address']
    country = request.form['country']
    city = request.form['city']
    state = request.form['state']
    postal_code = request.form['postal_code']
    additional_address = request.form['additional_address']
    phone = request.form['phone']
    status = "Active"

    # Generate a unique ID for the patient
    patient_id = generate_patient_id()

  
    insert_login = "INSERT INTO login (username, password, user_type) VALUES ('%s', '%s', 'patient')" % (email, password)

    login_id= insert(insert_login)
    print("Login id",login_id)
    
    insert_sql = "INSERT INTO patients (patient_id,login_id,first_name, last_name, email, date_of_birth, gender, address, country, city, state, postal_code, additional_address, phone, status) VALUES ('%s','%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (
    patient_id,login_id,first_name, last_name, email, date_of_birth, gender, address, country, city, state, postal_code, additional_address, phone, status)  
    
    msg = Message('Registration Successful! HMS Team', sender = 'rinshaaisha1422001@gmail.com', recipients =[email] )
    msg.body =  f'''
                <h1>Hello {first_name},</h1>
                <p>Thank you for registering with our service. We are excited to have you on board.</p>
                <p>Your login details are:</p>
                <ul>
                    <li><strong>Username:</strong> {email}</li>
                    <li><strong>Password:</strong> {password}</li>
                </ul>
                <p>Please keep your login details safe and do not share them with anyone.</p>
                <p>Best regards,<br>The HMS Team</p>
            </body>
            </html>
            '''
    mail = Mail(current_app)
    mail.send(msg)


    insert(insert_sql)


    
    return render_template('login.html')
    


@public.route('/appointment')
def appointment():

    return render_template('view_appointment.html')


@public.route('/forgot_password')
def forgot_password():
    return render_template('forgot_password.html')
    
@public.route('/forgot_password_get', methods=['POST'])
def forgot_password_get():
    email = request.form['email']
    print(email)

    # Check if the email exists in the database before proceeding
    check_email_query = f"SELECT COUNT(*) as count FROM login WHERE username='{email}' AND user_type='patient'"
    result = select(check_email_query)
    email_count = result[0]['count']

    if email_count == 0:
        # Email not found in the database, display a custom error flash message
        flash("The provided email does not exist in our records.", category="error")
        return redirect(url_for('public.forgot_password'))

    # The email exists in the database, proceed with sending the reset password email
    select_password = f"SELECT password FROM login WHERE username='{email}' AND user_type='patient'"
    res = select(select_password)

    if res:
        last_password_dict = res[-1]
        last_password = last_password_dict['password']
        # Save the password to a variable
        password = last_password

        msg = Message('Forgot Password - HMS', sender='rinshaaisha1422001@gmail.com', recipients=[email])
        msg.body = f'''
            <body>
            <h1>Hello {email},</h1>
            <p>We received a request to reset your password for the HMS service.</p>
            <p>Your login details are:</p>
            <ul>
                <li><strong>Username:</strong> {email}</li>
                <li><strong>Password:</strong> {password}</li>
            </ul>
            <p>Best regards,<br>The HMS Team</p>
        '''

        mail = Mail(current_app)
        mail.send(msg)

    # Flash a success message to indicate the reset password email has been sent
    flash("An email with your login details has been sent.", category="success")

    return redirect(url_for('public.forgot_password'))