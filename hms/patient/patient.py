from flask import Blueprint,render_template,request,redirect,flash,session,url_for,send_from_directory,send_file,json
from hms.database import *
from datetime import datetime
import random
import string
from flask_mail import Message
from flask_mail import Mail, Message
from flask import Blueprint, current_app
import uuid 
from flask_mail import Mail, Message
from hms.s3_function import *
from datetime import datetime, timedelta
# from twilio.rest import Client

# Keras
import numpy as np
import os
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

# Flask utils
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
public = Blueprint('public', __name__)

# Model saved with Keras model.save()
MODEL_PATH = 'models/modelres50.h5'

#Load your trained model
model = load_model(MODEL_PATH)

print('Model loaded. Start serving...')

patient = Blueprint('patient',__name__)


@patient.route('/images/<filename>')
def get_image(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

@patient.route('/patient_home')
def patient_home():

    login_id = session.get('login_id')

    print("login_idvdvedv",login_id)
    select_doctor = "SELECT * FROM doctor where status='Active'"
    doctor = select_2(select_doctor)


    select_dep = "SELECT * FROM department"
    department = select_2(select_dep)

    # Combine doctor and department data
    for doc in doctor:
        doc_department_id = doc['dep_id']
        department_name = next((dept['dep_name'] for dept in department if dept['dep_id'] == doc_department_id), 'Unknown Department')
        doc['department_name'] = department_name

    print(doctor)
    return render_template('patient_home.html',doctor=doctor)



@patient.route('/email')
def email():
    msg = Message('Hello from the other side!', sender =   'suhailshaji@gmail.com', recipients = ['suhailshaji007@gmail.com'])
    msg.body = "Hey this is a text msg from hms"
    mail = Mail(current_app)
    mail.send(msg)
    return "Message sent!"


@patient.route('/online_lab', methods=['GET'])
def onlinelab():
    login_id = session.get('login_id')
    return render_template('detection_index.html')




def model_predict(img_path, model):
    img = image.load_img(img_path, target_size=(200,200)) #target_size must agree with what the trained model expects!!

    # Preprocessing the image
    img = image.img_to_array(img)
    img = np.expand_dims(img, axis=0)
    img = img.astype('float32')/255
   
    preds = model.predict(img)

   
   
    pred = np.argmax(preds,axis = 1)
    return pred





@patient.route('/predict', methods=['POST'])
def upload():
    login_id = session.get('login_id')
    print("Login_ID",login_id)
    select_doctor = "SELECT * FROM doctor where dep_id =10"
    doctor = select_2(select_doctor)

    if request.method == 'POST':
        # Get the file from the POST request
        f = request.files['file']

        # Generate a random string and append it to the filename
        random_string = str(uuid.uuid4().hex)
        file_extension = f.filename.split('.')[-1]
        new_filename = secure_filename(f.filename.replace(file_extension, f"{random_string}.{file_extension}"))

        # # Save the file to the server
        # basepath = os.path.dirname(__file__)
        SUBFOLDER_NAME='MRI_images'
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'],SUBFOLDER_NAME, new_filename)
        f.save(file_path)
        print("FilePath",new_filename)

        # Make prediction using your model_predict() function
        pred = model_predict(file_path, model)
        # os.remove(file_path)  # Remove the file from the server after prediction

        # raw_image = upload_to_s3(f)
        
         # Arrange the correct return according to the model. 
        str0 = 'Glioma'
        str1 = 'Meningioma'
        str3 = 'pituitary'
        str2 = 'No Tumour'
        if pred[0] == 0:
            detection =str0
        elif pred[0] == 1:
            detection =str1
        elif pred[0]==3:
            detection =str3
        else:
            detection =str2


    return render_template('result_preview.html',detection=detection,login_id=login_id,doctor=doctor,file_path=new_filename)

# Add other routes for remaining pages


@patient.route('/view_prescription_pdf',methods=['GET'])
def view_prescription_pdf():
    appointment_id =request.args['id']
    print(appointment_id)

      # Assuming the file name is the same as the appointment ID and located in the UPLOAD_FOLDER/pdf directory
    filename = f'{appointment_id}.pdf'
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'pdf', filename)

    # Check if the file exists before sending it
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=False)
    else:
        return "Prescription not found."


def generate_time_slots(start_time, end_time, interval_minutes=30):
    current_time = start_time
    time_slots = []

    while current_time <= end_time:
        time_slots.append(current_time.strftime('%H:%M'))
        current_time += timedelta(minutes=interval_minutes)

    return time_slots

@patient.route('/make_booking_direct/<int:doc_id>/', methods=['GET'])
def make_booking_direct(doc_id):
    login_id = session.get('login_id')
    print("Login_ID",login_id)

    print("doctor_id for booking",doc_id)
    select_dep = f"SELECT * FROM doctor where doc_id='{doc_id}'"
    doctor = select_2(select_dep)
    print(doctor)
    print("Login ID:", login_id)
    select_patient = f"SELECT * FROM patients WHERE login_id='{login_id}'"
    patient = select_2(select_patient)
    print("Patient Data:", patient)

     # Fetch the appointment data for the selected doctor
    select_appointments = f"SELECT appointment_date, appointment_time FROM appointment WHERE doctor_id='{doc_id}'AND appointment_date >= CURDATE()"
    appointments = select_2(select_appointments)
    print("Appointments Data:", appointments)
    booked_slots = {}  # Dictionary to store booked slots by date

    # Organize booked slots by date
    for appointment in appointments:
        date = appointment['appointment_date'].strftime('%Y-%m-%d')
        time = (datetime.min + appointment['appointment_time']).time().strftime('%H:%M')  # Convert timedelta to time and then format
        
        if date not in booked_slots:
            booked_slots[date] = []
        booked_slots[date].append(time)

    print("booked slot",booked_slots)
    # Calculate available time slots for each date
    doctor_availability = {}  # Dictionary to store availability by date

    start_time = datetime.strptime('09:00', '%H:%M')
    end_time = datetime.strptime('17:00', '%H:%M')

    current_date = datetime.now().date()  # You can replace this with the desired date

    while current_date <= (datetime.now().date() + timedelta(days=30)):  # Consider the next 30 days
        current_date_str = current_date.strftime('%Y-%m-%d')

        if current_date_str in booked_slots:
            booked_times = booked_slots[current_date_str]
            available_slots = [time for time in generate_time_slots(start_time, end_time) if time not in booked_times]
        else:
            available_slots = generate_time_slots(start_time, end_time, interval_minutes=30)


        doctor_availability[current_date_str] = available_slots

        current_date += timedelta(days=1)
    
    print("doctor_availability", doctor_availability)
    return render_template('booking_direct.html', patient=patient,  doctor=doctor, doctor_availability=doctor_availability)


@patient.route('/make_booking/<int:login_id>/<string:detection>/<int:doc_id>/<string:file_path>', methods=['GET'])
def make_booking(login_id, detection, doc_id,file_path):
    print("Doctor ID:", doc_id)
    select_dep = f"SELECT * FROM doctor where doc_id='{doc_id}'"
    doctor = select_2(select_dep)
    print(doctor)
    print("Login ID:", login_id)
    select_patient = f"SELECT * FROM patients WHERE login_id='{login_id}'"
    patient = select_2(select_patient)
    print("Patient Data:", patient)
    print("File_Path -n Booking",file_path)

    


    return render_template('booking.html', patient=patient, detection=detection, doctor=doctor,file_path=file_path)




@patient.route('/make_appointment', methods=['POST'])
def make_appointment():
    # Get data from the form
    patient_id = request.form['patient_id']
    doctor_id = request.form['doctor_id']
    detection = request.form['detection']
    appointment_date = request.form['appointment_date']
    appointment_time = request.form['appointment_time']
    symptoms = request.form['symptoms']
    appointment_status="Active"
    MRI_file_path=request.form['file_path']
 

    # For demonstration purposes, let's print the data
    print("Patient ID:", patient_id)
    print("Doctor ID:", doctor_id)
    print("Detection:", detection)
    print("Appointment Date:", appointment_date)
    print("Appointment Time:", appointment_time)
    print("Symptoms:", symptoms) 

    select_patient = f"SELECT * FROM patients WHERE id='{patient_id}'"
    patient_list = select_2(select_patient)

    select_doctor = f"SELECT * FROM doctor WHERE doc_id='{doctor_id}'"
    doctor_list = select_2(select_doctor)

    if doctor_list:
        doctor =doctor_list[0]

        doctor_name=doctor['first_name']
        doctor_last_name=doctor['last_name']

    if patient_list:
        patient = patient_list[0]  # Get the first patient record (assuming there's only one patient with the given ID)
        print("Patient Data:", patient)

        patient_email = patient['email']
        patient_phone =patient['phone']
        patient_name = patient['first_name']
        print("Email:", patient_email)

    msg = Message(f'Appointment Confirmation with Dr.{doctor_name} ', sender = 'rinshaaisha1422001@gmail.com', recipients =[patient_email] )
    msg.body =  f'''<body>
            <h1>Hello {patient_name},</h1>
            <p>Your appointment has been scheduled successfully.</p>
            <p>Appointment Details:</p>
            <ul>
                <li>Doctor Name : {doctor_name}{doctor_last_name}</li>
                <li>Date: {appointment_date}</li>
                <li>Time: {appointment_time}</li>
            </ul>

            <p>We look forward to seeing you at the appointed time.</p>
            <p>Please don't hesitate to contact us if you have any questions or need to reschedule.</p>
            <p>Best regards,<br>The HMS Team</p>
        </body>
        </html>
        '''
    mail = Mail(current_app)
    mail.send(msg)



    # account_sid = 'AC0e488a8d13100aa9c45a11ef88ae93b3'
    # auth_token = '600b8923a7373f55383762e4398aeb86'
    # client = Client(account_sid, auth_token)

    # message = client.messages.create(
    # from_='+13187502645',
    # body=f' Hi {patient_name} Your appointment has been scheduled successfully on {appointment_date} with Dr. {doctor_name} {doctor_last_name   } ',
    # to='+919961049442'
    # )

    # print(message.sid)


    insert_appointment = "INSERT INTO appointment (patient_id,doctor_id,detection,appointment_date,appointment_time,symptoms,appointment_status,MRI_file_path)VALUES('%s','%s','%s','%s','%s','%s','%s','%s')"%(patient_id,doctor_id,detection,appointment_date,appointment_time,symptoms,appointment_status,MRI_file_path)

    insert(insert_appointment)


    # # You can redirect to a success page or render a confirmation template here
    # return render_template('confirmation.html',patient_id=patient_id,
    #                            doctor_id=doctor_id,
    #                            detection=detection,
    #                            appointment_date=appointment_date,
    #                            appointment_time=appointment_time,
    #                            symptoms=symptoms)

    return render_template('confirmed.html')

@patient.route('/cancel_appointment',methods=['GET'])
def cancel_appointment():
    appointment_id =request.args['id']

    delete_appointment= "DELETE FROM appointment WHERE appointment_id = %s"
    delete_data = (appointment_id,)
    delete2(delete_appointment, delete_data)

    return render_template('cancel.html')

@patient.route('/myappointment')
def myappointment():
    login_id = session.get('login_id')
    print("Login Id", login_id)

    select_patient = f"SELECT * FROM patients WHERE login_id = {login_id}"
    patient_data = select_2(select_patient)

    if not patient_data:
        # Handle the case when patient_data is empty
        print("No patient data found for the login_id:", login_id)
        return render_template("myappointment.html", appointment=[])

    # Access the patient_id from the patient data
    patient_id = patient_data[0]['id']

    # Printing the patient_id for verification (optional)
    print("Patient ID:", patient_id)

    appointment_select = f"SELECT * FROM appointment WHERE patient_id = {patient_id}"
    appointment = select_2(appointment_select)

    print(appointment)

    # Iterate through each appointment and fetch doctor details
    data = []
    for appointments_data in appointment:
        print(appointments_data)
        doctor_id = appointments_data['doctor_id']

        # Construct the doctor query
        doctor_query = f"SELECT * FROM doctor WHERE doc_id = '{doctor_id}'"

        # Assuming you have a function to execute the query and fetch results (e.g., select_2 function)
        doctor_query_result = select_2(doctor_query)
        if doctor_query_result:
            appointments_data.update(doctor_query_result[0])
            data.append(appointments_data)

    print("Appointments data:", data)

    return render_template("myappointment.html", appointment=data)


@patient.route('/edit_profile_patient')
def edit_profile_patient():
    login_id = session.get('login_id')
    print(login_id)

    patient = f"SELECT * FROM patients WHERE login_id='{login_id}'"
    patient_data = select_2(patient)
    print("doctor Data:", patient_data)

    name=patient_data[0]['first_name']
    login_id=patient_data[0]['login_id']
    print("-------",login_id)

    patient_login = f"SELECT * FROM login WHERE login_id='{login_id}'"
    patient_login=select_2(patient_login)
    print("login--",patient_login)



    return render_template('patient_editprofile.html',patient_data=patient_data,patient_login=patient_login)



@patient.route('/edit_patient_profile_get',methods=['POST'])
def edit_patient_profile():
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

    phone = request.form['phone']


      # Create the SQL query for the update operation with single quotes around the values
    query = f"UPDATE login SET username = '{email}', password = '{password}' WHERE login_id  = '{login_id}'"
    rows_affected = update(query)

    query_doctor = f"UPDATE patients SET address = '{address}',country = '{country}',city = '{city}',state = '{state}',postal_code = '{postal_code}' ,phone = '{phone}'  WHERE login_id  = '{login_id}'"
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
    return redirect(url_for('patient.edit_profile_patient'))



