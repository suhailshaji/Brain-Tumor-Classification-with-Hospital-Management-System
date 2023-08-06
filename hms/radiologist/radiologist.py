from flask import Blueprint,render_template,request,redirect,flash,session,url_for
from hms.database import *
from datetime import datetime
import random
import string
from flask_mail import Message
from flask_mail import Mail, Message
from flask import Blueprint, current_app
from datetime import date, timedelta
import numpy as np
import os
import uuid
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
# Flask utils
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
radiologist = Blueprint('radiologist',__name__)

# Model saved with Keras model.save()
MODEL_PATH = 'models/modelres50.h5'

#Load your trained model
model = load_model(MODEL_PATH)

print('Model loaded. Start serving...')


# Function to generate a random ID

@radiologist.route('/radiologist_home')
def radiologist_home():
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



    return render_template('radiologist_home.html',appointment_count=appointment_count,data=data,data_upcoming=data_upcoming)



@radiologist.route('/mri_home')
def mri_home():
    appointment_id =request.args['appointment_id']
    print("appointment_id",appointment_id)

    return render_template('radiologist_detection.html',appointment_id=appointment_id)



def model_predict(img_path, model):
    img = image.load_img(img_path, target_size=(200,200)) #target_size must agree with what the trained model expects!!

    # Preprocessing the image
    img = image.img_to_array(img)
    img = np.expand_dims(img, axis=0)
    img = img.astype('float32')/255
   
    preds = model.predict(img)

   
   
    pred = np.argmax(preds,axis = 1)
    return pred





@radiologist.route('/predict_mri_radiologist', methods=['POST'])
def predict_mri_radiologist():
    login_id = session.get('login_id')
    print("Login_ID",login_id)
    select_doctor = "SELECT * FROM doctor where dep_id =10"
    doctor = select_2(select_doctor)

    if request.method == 'POST':
        # Get the file from the POST request
        f = request.files['file']
        appointment_id =request.form['appointment_id']
        print("appointment_id",appointment_id)

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
            patient_email =patient_query[0]['email']
            appointments_data.update(patient_query[0])
            data_patient.append(appointments_data)

    
    # doctor_id=data_patient['doctor_id']
    print("dpcjkbndfjnv",doctor_id)
    select_dep = f"SELECT * FROM doctor where doc_id='{doctor_id}'"
    doctor = select_2(select_dep)
    print(doctor)
    for doctor in doctor:

        doctor_name=doctor['first_name'] 

    print("Appointment----",data_patient)

    print("email",patient_email)


    return render_template('radiologist_result_preview.html',doctor_name=doctor_name,detection=detection,appointment_id=appointment_id,file_path=new_filename,data_patient=data_patient,patient_email=patient_email)


@radiologist.route('/submit_mri_result',methods=['POST'])
def submit_mri_result():

    # Get the form data, including file_path, appointment_id, and detection
    file_path = request.form.get('file_path')
    appointment_id = request.form.get('appointment_id')
    detection = request.form.get('detection')
    patient_email=request.form.get('patient_email')

    print(file_path)
    print(appointment_id)
    print(detection)
    print("email",patient_email)
    

    query = f"UPDATE appointment SET detection = '{detection}', MRI_file_path = '{file_path}',appointment_status='Active' WHERE appointment_id  = '{appointment_id}'"
    rows_affected = update(query)

    msg = Message('Your MRI Result is Out ! HMS', sender='rinshaaisha1422001@gmail.com', recipients=[patient_email])
    msg.body = f'''
        <body>
        <h1>Hello {patient_email},</h1>
        <p>We are pleased to inform you that your MRI result is out with apppointment ID {appointment_id} (HMS).</p>
       
        <p>Best regards,<br>The HMS Team</p>
    '''

    mail = Mail(current_app)
    mail.send(msg)

    return redirect(url_for('radiologist.radiologist_home'))