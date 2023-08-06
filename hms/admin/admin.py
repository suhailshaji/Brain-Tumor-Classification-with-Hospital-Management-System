from flask import Blueprint,render_template,request,redirect,url_for
from hms.database import *
from datetime import datetime
import random
import string
from flask_mail import Message
from flask_mail import Mail, Message
from flask import Blueprint, current_app
from werkzeug.utils import secure_filename
import os


admin = Blueprint('admin',__name__)

# Function to generate a random ID
def generate_patient_id():
    prefix = "MRA"
    random_number = ''.join(random.choices(string.digits, k=5))
    return prefix + random_number


def generate_doctor_id():
    prefix = "DOC"
    random_number = ''.join(random.choices(string.digits, k=5))
    return prefix + random_number

def generate_receptionist_id():
    prefix = "EMP"
    random_number = ''.join(random.choices(string.digits, k=5))
    return prefix + random_number

def generate_radiologist_id():
    prefix = "RID"
    random_number = ''.join(random.choices(string.digits, k=5))
    return prefix + random_number


@admin.route('/admin_dashboard')
def index_admin():
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

    # Printing patient count and other patient data (if any)
    print("Patient Count:", patient_count)

    select_sql_dep = "SELECT *, (SELECT COUNT(*) FROM department) AS dep_count FROM department"
    department = select_2(select_sql_dep)

    # Extracting the patient count from the first row of the result
    if len(department) > 0:
        dep_count = department[0]['dep_count']
    else:
        # If no patients are found, set patient_count to 0
        dep_count = 0

    select_sql_receptionist = "SELECT *, (SELECT COUNT(*) FROM receptionist) AS receptionist_count FROM receptionist"
    receptionist = select_2(select_sql_receptionist)

    # Extracting the patient count from the first row of the result
    if len(receptionist) > 0:
        receptionist_count = receptionist[0]['receptionist_count']
    else:
        # If no patients are found, set patient_count to 0
        receptionist_count = 0

    # Printing patient count and other patient data (if any)
    print("Patient Count:", patient_count)
    return render_template('index_admin.html',patient_count=patient_count,doctor_count=doctor_count,receptionist_count=receptionist_count,dep_count=dep_count,doctor=doctor,patient=patients)
    

@admin.route('/admin_patient')
def admin_patient():
    select_sql = "SELECT * FROM patients"
    patients = select_2(select_sql)
    print(patients)

    
    
    return render_template('admin_patient.html', patients=patients)

@admin.route('/add_patient')
def add_patient():
    return render_template('add_patient.html')


@admin.route('/create_patient', methods=['POST'])
def create_patient():
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

    # Insert data into the database (code to be implemented)

    
    insert_sql = "INSERT INTO patients (patient_id,first_name, last_name, email, password, date_of_birth, gender, address, country, city, state, postal_code, additional_address, phone, status) VALUES ('%s','%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (
    patient_id,first_name, last_name, email, password, date_of_birth, gender, address, country, city, state, postal_code, additional_address, phone, status)

    insert(insert_sql)
    
    select_sql = "SELECT * FROM patients WHERE patient_id = %s"
    patient_details = select(select_sql, (patient_id,))

    print(patient_details)

    if patient_details:
        # Get the first row of the result (patient details)
        patient = patient_details[0]

        # Render the medical card template and pass the patient details
        return render_template('medical_card.html', patient=patient)
    else:
        return "Patient not found"


   
@admin.route('/view_patient_details_admin')
def view_patient():
    patient_id = request.args.get('id')
    print(patient_id)
    select_sql = "SELECT * FROM patients WHERE patient_id = %s"
    patient_details = select(select_sql, (patient_id,))

    print(patient_details)

    if patient_details:
        # Get the first row of the result (patient details)
        patient = patient_details[0]
    return render_template('medical_card.html', patient=patient)

@admin.route('/admin_receptionist')
def admin_receptionist():
    select_sql = "SELECT * FROM receptionist"
    receptionist = select_2(select_sql)
    print(receptionist)
  
    return render_template('admin_receptionist.html',receptionist=receptionist)

@admin.route('/add_receptionist')
def add_receptionist():
    return render_template('add_receptionist.html')

@admin.route('/delete_receptionist', methods=['GET'])
def delete_receptionist():
    # Get the receptionist ID from the URL query parameters
    receptionist_id = request.args.get('id')

    # Check if the receptionist exists in the database before proceeding with deletion
    receptionist_query = "SELECT * FROM receptionist WHERE receptionist_id = %s"
    receptionist=select(receptionist_query, (receptionist_id,))
    print("Receptionist",receptionist)

 
    receptionist_data = receptionist[0]  # Get the first (and only) dictionary from the list
    login_id = receptionist_data['login_id']
    delete_login_query = "DELETE FROM login WHERE login_id = %s"
    login_id = receptionist_data['login_id']
    delete_data = (login_id,)
    delete2(delete_login_query, delete_data)

    delete_receptionist_query = "DELETE FROM receptionist WHERE receptionist_id = %s"
    delete_data = (receptionist_id,)
    delete2(delete_receptionist_query, delete_data)

    # Redirect to the admin receptionist page after successful deletion
    # return render_template('index_admin.html')
    return redirect(url_for('admin.admin_receptionist'))


@admin.route('/delete_department',methods=['GET'])
def delete_department():

    dep_id = request.args.get('id')
    delete_department_query = "DELETE FROM department WHERE dep_id = %s"
    delete_data = (dep_id,)
    delete2(delete_department_query, delete_data)

    return redirect(url_for('admin.department_home'))
    
@admin.route('/change_status_dep_inactive',methods=['GET'])
def change_status_dep_inactive():
    dep_id =request.args.get('id')

    query = f"UPDATE department SET dep_status = 'Inactive' WHERE dep_id  = '{dep_id}'"
    rows_affected = update(query)

    return redirect(url_for('admin.department_home'))

@admin.route('/change_status_dep_active',methods=['GET'])
def change_status_dep_active():
    dep_id =request.args.get('id')

    query = f"UPDATE department SET dep_status = 'Active' WHERE dep_id  = '{dep_id}'"
    rows_affected = update(query)

    return redirect(url_for('admin.department_home'))

@admin.route('/change_status_doc_active',methods=['GET'])
def change_status_doc_active():
    doc_id =request.args.get('id')

    query = f"UPDATE doctor SET status = 'Active' WHERE doc_id  = '{doc_id}'"
    rows_affected = update(query)

    return redirect(url_for('admin.admin_view_doctor'))

@admin.route('/change_status_doc_inactive',methods=['GET'])
def change_status_doc_inactive():
    doc_id =request.args.get('id')

    query = f"UPDATE doctor SET status = 'Inactive' WHERE doc_id  = '{doc_id}'"
    rows_affected = update(query)

    return redirect(url_for('admin.admin_view_doctor'))


@admin.route('/change_status_receptionist_active',methods=['GET'])
def change_status_receptionist_active():
    id= request.args.get('id')

    query = f"UPDATE receptionist SET status = 'Active' WHERE id  = '{id}'"
    rows_affected = update(query)

    return redirect(url_for('admin.admin_receptionist'))

@admin.route('/change_status_receptionist_inactive',methods=['GET'])
def change_status_receptionist_inactive():
    id= request.args.get('id')

    query = f"UPDATE receptionist SET status = 'Inactive' WHERE id  = '{id}'"
    rows_affected = update(query)

    return redirect(url_for('admin.admin_receptionist'))


@admin.route('/delete_doc',methods=['GET'])
def delete_doc():

    doc_id = request.args.get('id')
    delete_doctor_query = "DELETE FROM doctor WHERE doc_id = %s"
    delete_data = (doc_id,)
    delete2(delete_doctor_query, delete_data)

    return redirect(url_for('admin.admin_view_doctor'))

@admin.route('/create_receptionist', methods=['POST'])
def create_receptionist():
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
    receptionist_id = generate_receptionist_id()

    insert_login = "INSERT INTO login (username, password, user_type) VALUES ('%s', '%s', 'receptionist')" % (email, password)

    login_id= insert(insert_login)
    print("Login id",login_id)
    
    insert_sql = "INSERT INTO receptionist (receptionist_id,login_id,first_name, last_name, email, date_of_birth, gender, address, country, city, state, postal_code, additional_address, phone, status) VALUES ('%s','%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (
    receptionist_id,login_id,first_name, last_name, email, date_of_birth, gender, address, country, city, state, postal_code, additional_address, phone, status)

    insert(insert_sql)
    
    return render_template('index_admin.html')




@admin.route('/admin_doctor')
def admin_view_doctor():
    select_sql = "SELECT * FROM doctor"
    doctor = select_2(select_sql)
    print(doctor)

    
    return render_template('admin_doctor.html',doctor=doctor)

@admin.route('/add_doctor')
def add_doctor():

    select_sql = "SELECT * FROM department"
    deps = select_2(select_sql)
    print(deps)
    
    return render_template('add_doctor.html',deps=deps)


@admin.route('/deparment_home')
def department_home():
    select_sql = "SELECT * FROM department"
    dep = select_2(select_sql)
    print(dep)
    return render_template('view_department.html',dep=dep)

@admin.route('/add_department')
def add_dep():
    return render_template('add_department.html')



@admin.route('/create_deparment',methods=['POST'])
def create_department_form():

    dep_name =request.form['dep_name']
    dep_status =request.form['dep_status']

    insert_dep = "INSERT INTO department (dep_name, dep_status) VALUES ('%s', '%s')" % (dep_name, dep_status)

    insert(insert_dep)

    return redirect(url_for('admin.department_home'))


@admin.route('/create_doctor', methods=['POST'])
def add_doctor_form():
     # Retrieve form data
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    password = request.form['password']
    date_of_birth = datetime.strptime(request.form['date_of_birth'], '%d-%m-%Y').strftime('%Y-%m-%d')
    gender = request.form['gender']
    qualification=request.form['qualification']
    address = request.form['address']
    country = request.form['country']
    city = request.form['city']
    state = request.form['state']
    postal_code = request.form['postal_code']
    additional_address = request.form['additional_address']
    phone = request.form['phone']
    status = request.form['status']
    dep_id =request.form['dep_id']
    profile_image = request.files['profile_image']
    save_path='test'
    # filename = secure_filename(profile_image.filename)
    # save_path = "/Users/suhail/Documents/project/Hospital Management System/hms/upload/dr-images/" + filename
    # # profile_image.save(save_path)



    

    # Generate a unique ID for the patient
    doctor_id = generate_doctor_id()

    # Insert data into the database (code to be implemented)
    insert_login = "INSERT INTO login (username, password, user_type) VALUES ('%s', '%s', 'doctor')" % (email, password)

    login_id= insert(insert_login)
    print("Login id",login_id)
    
    # insert_sql = "INSERT INTO doctor (login_id,doctor_id,first_name, last_name, email, date_of_birth, gender, address, country, city, state, postal_code, additional_address, phone, status) VALUES ('%s','%s','%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (
    # login_id,doctor_id,first_name, last_name, email, date_of_birth, gender, address, country, city, state, postal_code, additional_address, phone, status)
    insert_sql = "INSERT INTO doctor (login_id, doctor_id,dep_id, first_name, last_name, email, date_of_birth, qualification,gender, address, country, city, state, postal_code, additional_address, phone, status,image_filename) VALUES ('%s','%s','%s', '%s', '%s','%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s','%s')"%(login_id, doctor_id, dep_id,first_name, last_name, email, date_of_birth, qualification,gender, address, country, city, state, postal_code, additional_address, phone, status,save_path)



    insert(insert_sql)

    # select_sql = "SELECT * FROM doctor WHERE doctor_id = %s"
    # patient_details = select(select_sql, (doctor_id,))

    # print(patient_details)

    # if patient_details:
    #     # Get the first row of the result (patient details)
    #     patient = patient_details[0]

    #     # Render the medical card template and pass the patient details
    #     return render_template('medical_card.html', patient=patient)
    # else:
    #     return "Patient not found"
    
    return render_template('add_doctor.html')


@admin.route('/admin_radiologist')
def admin_radiologist():
    select_sql = "SELECT * FROM radiologist"
    radiologist = select_2(select_sql)
    print(radiologist)
    return render_template('admin_radiologist.html',radiologist=radiologist)


@admin.route('/add_radiologist')
def add_radiologist():
   
    return render_template('add_radiologist.html')

@admin.route('/create_radiologist', methods=['POST'])
def create_radiologist():
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
    radiologist_status = request.form['status']

    # Generate a unique ID for the patient
    radiologist_id = generate_radiologist_id()

    insert_login = "INSERT INTO login (username, password, user_type) VALUES ('%s', '%s', 'radiologist')" % (email, password)

    login_id= insert(insert_login)
    print("Login id",login_id)
    
    insert_sql = "INSERT INTO radiologist (radiologist_id,login_id,first_name, last_name, email, date_of_birth, gender, address, country, city, state, postal_code, additional_address, phone, radiologist_status) VALUES ('%s','%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (
    radiologist_id,login_id,first_name, last_name, email, date_of_birth, gender, address, country, city, state, postal_code, additional_address, phone, radiologist_status)

    insert(insert_sql)
    
    return redirect(url_for('admin.admin_radiologist'))




@admin.route('/change_status_radiologist_active',methods=['GET'])
def change_status_radiologist_active():
    id= request.args.get('id')

    query = f"UPDATE radiologist SET radiologist_status	 = 'Active' WHERE id  = '{id}'"
    rows_affected = update(query)

    return redirect(url_for('admin.admin_radiologist'))



@admin.route('/change_status_radiologist_inactive',methods=['GET'])
def change_status_radiologist_inactive():
    id= request.args.get('id')

    query = f"UPDATE radiologist SET radiologist_status	 = 'Inactive' WHERE id  = '{id}'"
    rows_affected = update(query)

    return redirect(url_for('admin.admin_radiologist'))


@admin.route('/delete_radiologist',methods=['GET'])
def delete_radiologist():
    id = request.args.get('id')
    delete_doctor_query = "DELETE FROM radiologist WHERE id = %s"
    delete_data = (id,)
    delete2(delete_doctor_query, delete_data)

    return redirect(url_for('admin.admin_radiologist'))