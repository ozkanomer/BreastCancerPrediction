from wtforms import Form, StringField, IntegerField

# Patients Register Form
class PatientsForm(Form):
    patientTc = IntegerField("Patient ID Number")
    patientName = StringField("Patient Name")
    patientAge = IntegerField("Patient Age")
    patientCity = StringField("Patient City")

