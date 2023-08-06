from flask import Blueprint,render_template,request,redirect,flash,session,url_for,jsonify
from hms.database import *
from datetime import datetime
import random
import string
from flask_mail import Message
from flask_mail import Mail, Message
from flask import Blueprint, current_app
from datetime import date, timedelta


receptionist = Blueprint('receptionist',__name__)



def generate_patient_id():
    prefix = "MRA"
    random_number = ''.join(random.choices(string.digits, k=5))
    return prefix + random_number

@receptionist.route('/receptionist_home')
def receptionist_home():

    login_id = session.get('login_id')

    print("login_Id",login_id)
    select_receptionist = "SELECT * FROM receptionist where status='Active'"
    receptionist = select_2(select_receptionist)

    select_sql = "SELECT *, (SELECT COUNT(*) FROM patients) AS patient_count FROM patients"
    patients = select_2(select_sql)

    # Extracting the patient count from the first row of the result
    if len(patients) > 0:
        patient_count = patients[0]['patient_count']
    else:
        # If no patients are found, set patient_count to 0
        patient_count = 0

    # Printing patient count and other patient data (if any)
    print("Patient Count:", patient_count)

    select_sql_doctor = "SELECT *, (SELECT COUNT(*) FROM doctor) AS doctor_count FROM doctor"
    doctor = select_2(select_sql_doctor)

    # Extracting the patient count from the first row of the result
    if len(doctor) > 0:
        doctor_count = doctor[0]['doctor_count']
    else:
        # If no patients are found, set patient_count to 0
        doctor_count = 0

    return render_template('receptionist_home.html',patient_count=patient_count,doctor_count=doctor_count)



@receptionist.route('/receptionist_patient')
def receptionist_patient():
    select_sql = "SELECT * FROM patients"
    patients = select_2(select_sql)
    print(patients)  
    return render_template('receptionist_patient.html', patients=patients)


@receptionist.route('/receptionist_add_patient')
def receptionist_add_patient():

    return render_template('receptionist_add_patient.html')

@receptionist.route('/receptionist_create_patient',methods=['POST'])
def receptionist_create_patient():
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
    status = request.form['status']

    # Generate a unique ID for the patient
    patient_id = generate_patient_id()

  
    insert_login = "INSERT INTO login (username, password, user_type) VALUES ('%s', '%s', 'patient')" % (email, password)

    login_id= insert(insert_login)
    print("Login id",login_id)
    
    insert_sql = "INSERT INTO patients (patient_id,login_id,first_name, last_name, email, date_of_birth, gender, address, country, city, state, postal_code, additional_address, phone, status) VALUES ('%s','%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (
    patient_id,login_id,first_name, last_name, email, date_of_birth, gender, address, country, city, state, postal_code, additional_address, phone, status)

    insert(insert_sql)

    msg = Message('Registration Successful! HMS Team', sender = 'rinshaaisha1422001@gmail.com', recipients =[email] )
    msg.body =  f'''
                <h1>Hello {first_name},</h1>
                <h2>Your Patient ID : {patient_id}</h2>
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

    
    return redirect(url_for('receptionist.receptionist_patient'))


   
@receptionist.route('/view_patient_details_receptionist')
def view_patient_details_receptionist():
    patient_id = request.args.get('id')
    print(patient_id)
    select_sql = "SELECT * FROM patients WHERE patient_id = %s"
    patient_details = select(select_sql, (patient_id,))

    print(patient_details)

    if patient_details:
        # Get the first row of the result (patient details)
        patient = patient_details[0]
    return render_template('receptionist_medical_card.html', patient=patient)

@receptionist.route('/delete_patient_details_receptionist', methods=['GET'])
def delete_patient_details_receptionist():
    # Get the receptionist ID from the URL query parameters
    patient_id = request.args.get('id')

     # Check if the receptionist exists in the database before proceeding with deletion
    patient_query = "SELECT * FROM patients WHERE patient_id = %s"
    patient = select(patient_query, (patient_id,))
    print("patient", patient)

    patient_data = patient[0]  # Get the first (and only) dictionary from the list
    login_id = patient_data['login_id']

    delete_login_query = "DELETE FROM login WHERE login_id = %s"
    delete_login_data = (login_id,)
    delete2(delete_login_query, delete_login_data)

    delete_patient_query = "DELETE FROM patients WHERE patient_id = %s"
    delete_patient_data = (patient_id,)
    delete2(delete_patient_query, delete_patient_data)
    # Redirect to the admin receptionist page after successful deletion
    # return render_template('index_admin.html')
    return redirect(url_for('receptionist.receptionist_patient'))


@receptionist.route('/search_patient', methods=['GET', 'POST'])
def search_patient():
    if request.method == 'POST':
        search_term = request.form.get('search_term')

        print("serach Term",search_term)

        # SQL query to search for patients based on name, email, or ID
        query = "SELECT * FROM patients WHERE first_name LIKE %s OR email LIKE %s OR patient_id = %s"
        search_pattern = f"%{search_term}%"  # Adding '%' to search for partial matches

        # Call the select_2 function to execute the query
        search = select_2(query, (search_pattern, search_pattern, search_term))

        print("Result from search",search)


        if search:
        # Get the first row of the result (patient details)
            patient = search[0]
            return render_template('receptionist_medical_card.html', patient=patient)
        else:
            flash('No records found', 'custom_warning')
            # Redirect to the 'receptionist_patient.html' page
            return redirect(url_for('receptionist.receptionist_patient'))

    return render_template('receptionist_patient.html')


@receptionist.route('/receptionist_appointment')
def receptionist_appointment():
    select_sql = "SELECT * FROM doctor"
    doctor = select_2(select_sql)
    print(doctor)
    
    return render_template('receptionist_appointment_create.html',doctor=doctor)



@receptionist.route('/get_patient_details', methods=['GET'])
def get_patient_details():
    search_term = request.args.get('search_term')

    # SQL query to search for patients based on name, email, or ID
    query = "SELECT * FROM patients WHERE first_name LIKE %s OR email LIKE %s OR phone = %s"
    search_pattern = f"%{search_term}%"

    patient = select_2(query, (search_pattern, search_pattern, search_term))

    print("Result from search",patient)

    return jsonify(patient)


@receptionist.route('/create_appointment', methods=['POST'])
def create_appointment():
 # Get data from the form
    patient_id = request.form['patient_id']
    doctor_id = request.form['doctor_id']
    appointment_date = request.form['appointment_date']
    appointment_time = request.form['appointment_time']

    appointment_status="Active"
 

    # For demonstration purposes, let's print the data
    print("Patient ID:", patient_id)
    print("Doctor ID:", doctor_id)

    print("Appointment Date:", appointment_date)
    print("Appointment Time:", appointment_time)


    insert_appointment = "INSERT INTO appointment (patient_id,doctor_id,appointment_date,appointment_time,appointment_status)VALUES('%s','%s','%s','%s','%s')"%(patient_id,doctor_id,appointment_date,appointment_time,appointment_status)

    insert(insert_appointment)

    return redirect(url_for('receptionist.receptionist_appointment_master'))

    


@receptionist.route('/receptionist_appointment_master')
def receptionist_appointment_master():
    today = date.today()

# Format 'today' as a string in YYYY-MM-DD format to use in the SQL query
    formatted_today = today.strftime('%Y-%m-%d')
    print("formatted",formatted_today)

    # Fetch appointments for the specific doc_id for Today
    # appointment_query = f"SELECT * FROM appointment WHERE doctor_id={doc_id} and appointment_status='Active'"
    appointment_query = f"SELECT * FROM appointment WHERE  appointment_status='Active' AND appointment_date='{formatted_today}'"
    appointments = select_2(appointment_query)

    appointment_count=len(appointments)
    print("count",appointment_count)

    # Iterate through each appointment and fetch patient details
    data = []
    for appointment in appointments:
        
        print(appointment)
        patient_id = appointment['patient_id']

        # Construct the patient query
        patient_query = f"SELECT * FROM patients WHERE id='{patient_id}'"

        # Assuming you have a function to execute the query and fetch results (e.g., select_2 function)
        patient = select_2(patient_query)
        appointment.update(patient[0])
        data.append(appointment)

    #Upcoming List

    # Add one day to 'today' to get the next day
    next_day = today + timedelta(days=1)

    # Format 'next_day' as a string in YYYY-MM-DD format to use in the SQL query
    formatted_next_day = next_day.strftime('%Y-%m-%d')
    appointment_query_upcoming = f"SELECT * FROM appointment WHERE  appointment_status='Active' AND appointment_date>='{formatted_next_day}'"
    appointments_data_upcoming = select_2(appointment_query_upcoming)
   


    # Iterate through each appointment and fetch patient details
    data_upcoming = []
    for appointments_data_upcoming in appointments_data_upcoming:
        
        print(appointments_data_upcoming)
        patient_id = appointments_data_upcoming['patient_id']

        
        # Construct the patient query
        patient_query_upcoming = f"SELECT * FROM patients WHERE id='{patient_id}'"

        # Assuming you have a function to execute the query and fetch results (e.g., select_2 function)
        patient_query_upcoming = select_2(patient_query_upcoming)
        appointments_data_upcoming.update(patient_query_upcoming[0])
        data_upcoming.append(appointments_data_upcoming)

    return render_template('receptionist_appointment_master.html',appointment_count=appointment_count,data=data,data_upcoming=data_upcoming)



@receptionist.route('/get_doctor_name', methods=['GET'])
def get_doctor_name():
    doctor_id = int(request.args.get('doctor_id'))
    doctor_name = "Doctor not found"

    select_sql = "SELECT * FROM doctor"
    doctors = select_2(select_sql)
    print(doctors)
    
    for doctor in doctors:
        if doctor['doc_id'] == doctor_id:
            doctor_name = f"{doctor['first_name']} {doctor['last_name']}"
            break
   
    return jsonify({"name": doctor_name})


@receptionist.route('/view_all_appointment')
def view_all_appointment():

    appointment_query = f"SELECT * FROM appointment WHERE  appointment_status='Active'"
    appointments = select_2(appointment_query)


    print("fetch",appointments)

    
    # Iterate through each appointment and fetch patient details
    data = []
    for appointment in appointments:
        
        print(appointment)
        patient_id = appointment['patient_id']

        # Construct the patient query
        patient_query = f"SELECT * FROM patients WHERE id='{patient_id}'"

        # Assuming you have a function to execute the query and fetch results (e.g., select_2 function)
        patient = select_2(patient_query)
        appointment.update(patient[0])
        data.append(appointment)



    return render_template('receptionist_view_all_appointment.html',data=data)



@receptionist.route('/delete_appointment', methods=['GET'])
def delete_appointment():

    id = request.args.get('id')
    print(id)

    delete_patient_query = "DELETE FROM appointment WHERE 	appointment_id = %s"
    delete_patient_data = (id,)
    delete2(delete_patient_query, delete_patient_data)

    return redirect(url_for('receptionist.view_all_appointment'))

