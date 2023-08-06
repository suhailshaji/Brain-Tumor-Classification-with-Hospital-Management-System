from flask import Flask, render_template
from flask_mail import Mail, Message






def create_app():

    app = Flask(__name__)
    app.config['DEBUG'] = True
    app.secret_key = 'your_secret_key'
    # Set the path to the directory containing the images
    app.config['UPLOAD_FOLDER'] = '/Users/suhail/Documents/project/Hospital Management System/hms/static'
    app.static_folder = '/Users/suhail/Documents/project/Hospital Management System/hms/static'
    app.config['MAIL_SERVER']='smtp-relay.brevo.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USERNAME'] = 'suhailshaji.works@gmail.com'
    app.config['MAIL_PASSWORD'] = 'xsmtpsib-bab19e8dbd7e991c745dcd9785dd480db0bac7c68b2c87155770e3bfded123b8-MSFL70B3GQXyx89v'
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False


    mail = Mail(app)

    from hms.admin.admin import admin
    from hms.public.public import public
    from hms.patient.patient import patient
    from hms.doctor.doctor import doctor
    from hms.receptionist.receptionist import receptionist
    from hms.radiologist.radiologist import radiologist 
  


    app.register_blueprint(admin)
    app.register_blueprint(public)
    app.register_blueprint(patient)
    app.register_blueprint(doctor)
    app.register_blueprint(receptionist)
    app.register_blueprint(radiologist)
    return app   