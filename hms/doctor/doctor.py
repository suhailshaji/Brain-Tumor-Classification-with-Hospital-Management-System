from flask import Blueprint,render_template,request,redirect,url_for,session,jsonify,flash
from hms.database import *
from datetime import datetime
import random
import datetime
import string
from flask_mail import Message
from flask_mail import Mail, Message
from flask import Blueprint, current_app
from werkzeug.utils import secure_filename
import os
from datetime import date, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

doctor = Blueprint('doctor',__name__)


@doctor.route('/doctor_home')
def doctor_home():

    login_id = session.get('login_id')
    print(login_id)

    doctor = f"SELECT * FROM doctor WHERE login_id='{login_id}'"
    doctor_data = select_2(doctor)
    print("doctor Data:", doctor_data)

    doc_id = doctor_data[0]['doc_id']
    print("Doctor_id",doc_id)
    today = date.today()

# Format 'today' as a string in YYYY-MM-DD format to use in the SQL query
    formatted_today = today.strftime('%Y-%m-%d')
    print("formatted",formatted_today)

    # Fetch appointments for the specific doc_id for Today
    # appointment_query = f"SELECT * FROM appointment WHERE doctor_id={doc_id} and appointment_status='Active'"
    appointment_query = f"SELECT * FROM appointment WHERE doctor_id={doc_id} AND appointment_status='Active' AND appointment_date='{formatted_today}'"
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
    appointment_query_upcoming = f"SELECT * FROM appointment WHERE doctor_id={doc_id} AND appointment_status='Active' AND appointment_date>='{formatted_next_day}'"
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

   
    

    return render_template('doctor_home.html',appointment_count=appointment_count,data=data,data_upcoming=data_upcoming)


@doctor.route('/get_appointment',methods=['GET'])
def get_appointment():
    get_appointment_id = request.args['appointment_id']

    appointment_select =f"SELECT * FROM appointment WHERE 	appointment_id={get_appointment_id} and appointment_status='Active'"
    appointment=select_2(appointment_select)

     # Iterate through each appointment and fetch patient details
    data_upcoming = []
    for appointments_data in appointment:
        
        print(appointments_data)
        patient_id = appointments_data['patient_id']

        # Construct the patient query
        patient_query = f"SELECT * FROM patients WHERE id='{patient_id}'"

        # Assuming you have a function to execute the query and fetch results (e.g., select_2 function)
        patient_query = select_2(patient_query)
        appointments_data.update(patient_query[0])
        data_upcoming.append(appointments_data)

        print("dfgrefgerh",data_upcoming)

    # old_appointment =f"SELECT * FROM appointment where patient_id={patient_id} AND appointment_status='Closed'"
    # old_appointment_data = select_2(old_appointment)
    # print("old data-----------",old_appointment_data)
    
    



    return render_template('doctor_view_appointment.html',data=data_upcoming)

def generate_prescription_pdf(patient_first_name, patient_last_name, patient_dob, patient_gender,
                              appointment_id, diagnosis, medicines, doctor_first_name, doctor_last_name, doctor_number,
                              pdf_file_path):
    doc = SimpleDocTemplate(pdf_file_path, pagesize=letter)
    styles = getSampleStyleSheet()

    # Custom styles
    header_style = ParagraphStyle(name="HeaderStyle", parent=styles["Title"], fontSize=16, textColor=colors.darkblue)
    patient_info_style = ParagraphStyle(name="PatientInfoStyle", parent=styles["Normal"], fontSize=12, leading=14)
    doctor_info_style = ParagraphStyle(name="DoctorInfoStyle", parent=styles["Normal"], fontSize=12, textColor=colors.darkgreen, leading=14)
    appointment_id_style = ParagraphStyle(name="AppointmentIDStyle", parent=styles["Normal"], fontSize=14, textColor=colors.blue)
    diagnosis_style = ParagraphStyle(name="DiagnosisStyle", parent=styles["Normal"], fontSize=14, textColor=colors.white, backColor=colors.darkblue, leading=18)
    medicine_table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ])

    story = []
    hospital_name = "HMS"

    # Current Date
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    date_para = Paragraph(f"<b>Date:</b> {current_date}", styles["Normal"])
    story.append(date_para)

    # Hospital Name
    hospital_heading = Paragraph(hospital_name, header_style)
    story.append(hospital_heading)

    # Patient and Doctor Information
    patient_doctor_info = f"<b>Patient Information:</b><br/>" \
                          f"Name: {patient_first_name} {patient_last_name}<br/>" \
                          f"Date of Birth: {patient_dob}<br/>" \
                          f"Gender: {patient_gender}<br/><br/>" \
                          f"<b>Doctor Information:</b><br/>" \
                          f"Name: Dr. {doctor_first_name} {doctor_last_name}<br/>" \
                          f"Phone: {doctor_number}"
    patient_doctor_info_para = Paragraph(patient_doctor_info, styles["Normal"])
    story.append(patient_doctor_info_para)

    # Appointment ID
    appointment_id_para = Paragraph(f'<br/><b>Appointment ID:</b> {appointment_id}', appointment_id_style)
    story.append(appointment_id_para)

    # Add space between Appointment ID and Diagnosis
    story.append(Spacer(1, 10))

    # Diagnosis
    diagnosis_para = Paragraph(f'<b>Diagnosis:</b><br/>{diagnosis}', diagnosis_style)
    story.append(diagnosis_para)

    # Medicines
    medicines_list = [med.strip() for med in medicines if med.strip()]
    if medicines_list:
        data = [["No", "Medicine", "Frequency"]]
        data += [[str(idx + 1), med.split("(")[0].strip(), med.split("(")[1].strip(")")] for idx, med in enumerate(medicines_list)]
        medicines_table = Table(data, colWidths=[40, 280, 100])
        medicines_table.setStyle(medicine_table_style)
        story.append(Spacer(1, 20))  # Adding more space before the table
        story.append(medicines_table)


    doc.build(story)



@doctor.route('/save_diagnosis_medicines', methods=['POST'])
def save_diagnosis_medicines():
    data = request.json
    appointment_id = data.get('appointment_id')
    diagnosis = data.get('diagnosis')
    # medicines = ', '.join(data.get('medicines'))  # Convert the list to a comma-separated string
    medicines_list = data.get('medicines')

    print("Appointment ID:", appointment_id)
    print("Diagnosis:", diagnosis)
    print("Medicines:", medicines_list)

    # Escape single quotes in the diagnosis and medicines to prevent SQL injection
    diagnosis = diagnosis.replace("'", "''")
       # Convert the list of dictionaries into a list of strings with name and frequency combined
    medicines = [f"{medicine['name']} ({medicine['frequency']})" for medicine in medicines_list]

    # Now, you can join the list of strings with a comma separator
    medicines_str = ', '.join(medicines)
    print("Medicines_str:", medicines_str)

    # Create the SQL query for the update operation with single quotes around the values
    query = f"UPDATE appointment SET diagnosis = '{diagnosis}', medicines = '{medicines_str}' ,appointment_status ='Closed' WHERE appointment_id  = '{appointment_id}'"

    # Call the update() function with the SQL query
    rows_affected = update(query)

    print("Rows affected:", rows_affected)

    print("Rows affected:", rows_affected)

    appointment_select =f"SELECT * FROM appointment WHERE 	appointment_id={appointment_id} "
    appointment=select_2(appointment_select)
    data_patient = []
    for appointments_data in appointment:
        
        print(appointments_data)
        patient_id = appointments_data['patient_id']

        doctor_id = appointments_data['doctor_id']

        # Construct the patient query
        patient_query = f"SELECT * FROM patients WHERE id='{patient_id}'"
        patient_query = select_2(patient_query)
        appointments_data.update(patient_query[0])
        data_patient.append(appointments_data)

    


    print("Appointment----",data_patient)

    patient_doc_id=data_patient[0]['doctor_id']
    doctor_query = f"SELECT * FROM doctor WHERE doc_id='{patient_doc_id}'"
    doctor_query = select_2(doctor_query)
    print("dvedv",doctor_query)



    patient_email=data_patient[0]['email']
    patient_first_name=data_patient[0]['first_name']
    patient_last_name=data_patient[0]['last_name']
    patient_gender=data_patient[0]['gender']
    patient_dob=data_patient[0]['date_of_birth']
    doctor_first_name=doctor_query[0]['first_name']
    doctor_last_name=doctor_query[0]['last_name']
    doctor_number=doctor_query[0]['phone']
    print(patient_email)
    SUBFOLDER_NAME='pdf'
    filename=f'{appointment_id}.pdf'
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'],SUBFOLDER_NAME,filename)

    pdf=generate_prescription_pdf(patient_first_name,patient_last_name,patient_dob,patient_gender,appointment_id,diagnosis,medicines,doctor_first_name,doctor_last_name,doctor_number,file_path)

    msg = Message('Prescription -HMS ', sender = 'rinshaaisha1422001@gmail.com', recipients =[patient_email] )
    msg.body =  f'''<body>
           <h1>Hello {patient_first_name},</h1>
            <p>Your Appointment ID: {appointment_id}</p>
            <p>Doctor Name:{doctor_first_name} {doctor_last_name}<p>
            <p>Doctor NO: {doctor_number}<p>
            <p>Diagnosis: {diagnosis}</p>
            <p>Prescribed Medicines:</p>
            <ul>
                {medicines}

            </ul>
            <p>Best regards,<br>The HMS Team</p>
        </body>
        </html>
        '''
    
    with current_app.open_resource(file_path) as fp:
        msg.attach(filename=filename, content_type='application/pdf', data=fp.read())
    mail = Mail(current_app)
    mail.send(msg)


    return jsonify({"message": "Data received successfully"}), 200





@doctor.route('/edit_profile')
def edit_profile():
    login_id = session.get('login_id')
    print(login_id)

    doctor = f"SELECT * FROM doctor WHERE login_id='{login_id}'"
    doctor_data = select_2(doctor)
    print("doctor Data:", doctor_data)

    name=doctor_data[0]['first_name']
    login_id=doctor_data[0]['login_id']
    print("-------",login_id)

    doctor_login = f"SELECT * FROM login WHERE login_id='{login_id}'"
    doctor_login=select_2(doctor_login)
    print("login--doctor",doctor_login)



    return render_template('doctor_editprofile.html',doctor_data=doctor_data,doctor_login=doctor_login)



@doctor.route('/edit_doctor_profile',methods=['POST'])
def edit_doctor_profile():
    login_id = session.get('login_id')
    print("vee",login_id)

    first_name = request.form['first_name']
    email = request.form['email']
    password = request.form['password']
    address = request.form['address']
    country = request.form['country']
    city = request.form['city']
    state = request.form['state']
    postal_code = request.form['postal_code']
    additional_address = request.form['additional_address']
    phone = request.form['phone']
    qualification=request.form['qualification']

      # Create the SQL query for the update operation with single quotes around the values
    query = f"UPDATE login SET username = '{email}', password = '{password}' WHERE login_id  = '{login_id}'"
    rows_affected = update(query)

    query_doctor = f"UPDATE doctor SET address = '{address}',  qualification = '{qualification}',country = '{country}',city = '{city}',state = '{state}',postal_code = '{postal_code}' ,phone = '{phone}'  WHERE login_id  = '{login_id}'"
    rows_affected = update(query_doctor)


    msg = Message('Profile has been Updated ', sender = 'rinshaaisha1422001@gmail.com', recipients =[email] )
    msg.body =  f'''<body>
            <h1>Hello Dr. {first_name},</h1>
            <p>Your Profile Has been Updated .</p>

            <p>Best regards,<br>The HMS Team</p>
        </body>
        </html>
        '''
    mail = Mail(current_app)
    mail.send(msg)

    flash("Your profile has been updated successfully.", category="success")
    return redirect(url_for('doctor.edit_profile'))



@doctor.route('/request_mri', methods=['POST'])
def request_mri():
    try:
        data = request.get_json()
        # Process the data, e.g., send an email notification or update the database
        # You can access data['appointment_id'] and data['patient_id'] here

        appointment_id=data['appointment_id']
        print(appointment_id)

        query = f"UPDATE appointment SET appointment_status='MRI_Request_Open' WHERE appointment_id  = '{appointment_id}'"
        rows_affected = update(query)
        print(rows_affected)
        # Return a response indicating success
        response = {'message': 'MRI request successful'}
        return jsonify(response), 200
    except Exception as e:
        # Handle errors and return an appropriate response
        return jsonify({'message': 'Error occurred', 'error': str(e)}), 500


@doctor.route('/request_view')
def request_view():
    today = date.today()

# Format 'today' as a string in YYYY-MM-DD format to use in the SQL query
    formatted_today = today.strftime('%Y-%m-%d')
    print("formatted",formatted_today)

    appointment_query = f"SELECT * FROM appointment WHERE  appointment_status='MRI_Request_Open' AND appointment_date='{formatted_today}'"
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
    appointment_query_upcoming = f"SELECT * FROM appointment WHERE  appointment_status='MRI_Request_Open' AND appointment_date>='{formatted_next_day}'"
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


    return render_template('doctor_mri_request.html',data=data)