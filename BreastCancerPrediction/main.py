from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
from flask_mysqldb import MySQL
from passlib.hash import sha256_crypt
from functools import wraps
import os.path
import pandas as pd

# Showing plot on web page
import matplotlib.pyplot as plt
import mpld3

# Load Functions and Classes
from TestForm import TestForm
from LoginForm import LoginForm
from PatientsForm import PatientsForm
from train import test # Test Function

# Login Session Decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("Please login to see this webpage!", "danger")
            return redirect(url_for("login"))
    return decorated_function


app = Flask(__name__)
app.secret_key = "bcppanel" # secret key for message flashing

# Flask MySQL Config
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "bcppanel"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)

# Home Page
@app.route("/")
def index():
    return render_template("index.html", title = "Home Page")

# Login Page
@app.route("/login", methods =["GET","POST"])
def login():
    form = LoginForm(request.form)

    if request.method == "POST":
        username = form.username.data
        password_entered = form.password.data
        
        # Create a cursor
        cursor = mysql.connection.cursor()

        # Username equal query
        query = "Select * From panelusers where tcID = %s"

        result = cursor.execute(query,(username,))
        
        # Close MySQL connection
        

        if result > 0:
            data = cursor.fetchone()
            real_password = data["password"]

            # Enter Success
            if sha256_crypt.verify(password_entered, real_password):
                flash("You Logged In Succesfully!", "success")

                # Change logged_in session
                session["logged_in"] = True
                session["username"] = username
                cursor.close()
                # Redirect Home Page
                return redirect(url_for("index"))
            else:
                # Enter Password Wrong
                flash("There is no user as you entered!", "danger")
                return redirect(url_for("login"))
        else:
            # Enter Username Wrong
            flash("There is no user as you entered.", "danger")
            return redirect(url_for("login"))
    # Normal Login Page
    return render_template("login.html", form = form, title = "Login Page")

# Logout
@app.route("/logout")
def logout():
    session.clear() # Clear Session
    flash("Logout Succesfully!", "success")
    return redirect(url_for("index"))

# Dashboard Page
@app.route("/dashboard", methods = ["GET", "POST"])
@login_required
def dashboard():
    # Create a cursor
    cursor = mysql.connection.cursor()   

    # total test query
    query_total = "SELECT * FROM patients"
    total = cursor.execute(query_total)

    # malignant patients query
    query_malignant = "SELECT * FROM patients WHERE patient_Diagnosis = %s"
    malignant = cursor.execute(query_malignant,("M",))

    # benign patients query
    query_benign = "SELECT * FROM patients WHERE patient_Diagnosis = %s"
    benign = cursor.execute(query_benign,("B",))
    
    
    # Close MySQL connection
    cursor.close()

    return render_template("dashboard.html", title = "Dashboard", total = total, malignant = malignant, benign = benign)

# Data Entry Page
@app.route("/data_entry", methods =["GET","POST"])
@login_required
def data_entry():
    # Create a cursor
    cursor = mysql.connection.cursor()
    query = "SELECT * FROM panelusers WHERE tcID = %s"
    cursor.execute(query,(session["username"],))

    # take all variables
    name = cursor.fetchall()

    # Close MySQL connection
    cursor.close()
    if request.method == "POST":
        pass

    return render_template("entry.html", title = "Data Entry", name = name[0]["name"], session = session)

# Petient Entry Page
@app.route("/patientEntry", methods = ["GET", "POST"])
@login_required
def patientEntry():
    form = PatientsForm(request.form)

    # If data send from the form
    if request.method == "POST":

        tc = form.patientTc.data
        name = form.patientName.data
        age = form.patientAge.data
        city = form.patientCity.data

        # Create a cursor
        cursor = mysql.connection.cursor()

        
        # Username equal query
        queryControl = "Select * From patients where patient_tc = %s"
        result = cursor.execute(queryControl,(tc,))

        # If patient already exist
        if result > 0:
            flash("Patient already exist!!!", "danger")
            return redirect(url_for("patientEntry"))
        else:
            # Write a query
            query = "INSERT into patients(patient_Tc,patient_Name,patient_age,patient_City) VALUES(%s,%s,%s,%s)"
            
            # Execute the cursor with query
            cursor.execute(query,(tc, name, age, city))
            mysql.connection.commit() # appy commits
            cursor.close() # Close mysql connection

            flash("Patient has been saved succesfully!", "success")
            return redirect(url_for("data_entry"))
    else:   
        return render_template("patientEntry.html", title = "Patient Entry Page", form = form)

@app.route("/patientSearch", methods = ["GET", "POST"])
@login_required
def patientSearch():

    # If method is POST
    if request.method == "POST":
        searchType = request.form.get("searchBy")
        keyword = request.form.get("searchBox")
        
        # Create MySQL Connection
        cursor = mysql.connection.cursor()
        
        # If user select searching by name
        if searchType == "name":
            NameQuery = "Select * from patients WHERE patient_Name like '%"+ keyword +"%'"
            result = cursor.execute(NameQuery)
            

            # If there was no patient
            if result == 0:
                flash("The patient you looking for has not found!", "danger")
                cursor.close() # Close mysql connection
                return render_template("patientSearch.html", title = "Search")

            # else more patients found
            else:
                patients = cursor.fetchall()
                cursor.close() # Close mysql connection
                return render_template("patientSearch.html", patients = patients, title = "Search")

        # else user select searching by ID Number
        else:
            IDquery = "Select * from patients WHERE patient_Tc like '%"+keyword+"%'"
            result = cursor.execute(IDquery)

            # If there was no patient
            if result == 0:
                flash("The patient you looking for has not found!", "danger")
                cursor.close() # Close mysql connection
                return render_template("patientSearch.html", title = "Search")
            
            # If patients found
            else:
                patients = cursor.fetchall()
                cursor.close() # Close mysql connection
                return render_template("patientSearch.html", patients = patients, title = "Search")
    
    # Normal Searc patient page
    return render_template("patientSearch.html", title = "Search")

# Dynamic Patient Page
@app.route("/addTest/<string:patient_Tc>", methods = ["GET", "POST"])
@login_required
def Patient(patient_Tc):

    # Create Test Form
    form = TestForm(request.form)

    # If post request
    if request.method == "POST":
        # Get Variables
        symptom = str(form.symptom.data)
        Clump_Thickness = form.Clump_Thickness.data
        uCell_Size = form.uCell_Size.data
        Cell_Shape = form.Cell_Shape.data
        Adhesion = form.Adhesion.data
        sCell_Size = form.sCell_Size.data
        Bare_Nuclei = form.Bare_Nuclei.data
        Bland_Chromatin = form.Bland_Chromatin.data
        Normal_Nucleoli = form.Normal_Nucleoli.data
        Mitoses = form.Mitoses.data

        # Create Test Array
        test_variables = [[Clump_Thickness, uCell_Size, Cell_Shape, Adhesion, sCell_Size, Bare_Nuclei, Bland_Chromatin, Normal_Nucleoli, Mitoses]]
        
        diagnosis = test(test_variables)
        if diagnosis == 1:
            d = "B"
        elif diagnosis == 0:
            d = "M"

       
        # Create MySQL Connection
        cursor = mysql.connection.cursor()

        # Write a query
        query = "INSERT into tests(patient_Tc,symptoms,test_Diagnosis,Clump_Thickness,Uniformity_of_Cell_size,Uniformity_of_Cell_Shape,Marginal_Adhesion,Single_Epithelial_Cell_Size,Bare_Nuclei,Bland_Chromatin,Normal_Nucleoli,Mitoses) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        UpdateDiagnosis = "UPDATE patients SET patient_Diagnosis = %s WHERE patient_Tc = %s"
        UpdateTestCount = "UPDATE patients SET patient_TestCount = %s WHERE patient_Tc = %s"
        TestCountQuery = "SELECT * From tests where patient_tc = %s"

        # Execute the cursor with query
        cursor.execute(query,(patient_Tc,symptom,d,Clump_Thickness,uCell_Size,Cell_Shape,Adhesion,sCell_Size,Bare_Nuclei,Bland_Chromatin,Normal_Nucleoli,Mitoses))
        mysql.connection.commit() # appy commits

        TestCount = cursor.execute(TestCountQuery,(patient_Tc,))
        cursor.execute(UpdateDiagnosis,(d,patient_Tc))
        cursor.execute(UpdateTestCount,(TestCount,patient_Tc))
        mysql.connection.commit() # appy commits
        cursor.close() # Close mysql connection

        flash("The test has been sent succesfully!", "success")
        return redirect(url_for("data_entry"))
    else:
        return render_template("PatientPage.html", form = form)

# addTest Page redirecting
@app.route("/addTest")
@login_required
def addTest():
    flash("There is no page you want to see!","danger")
    return redirect(url_for("index"))

# Program only works on terminal
if __name__ == "__main__":
    app.run(debug = True, host = "192.168.2.227") # Debug mode on