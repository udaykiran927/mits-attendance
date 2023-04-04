from flask import Flask,render_template,redirect,request,Response,make_response
from flask import send_file
import json
import pandas as pd
import pyrebase
from pathlib import Path
import os
import pickle


app=Flask(__name__)
df=pd.read_csv("class-merge.csv")
model=pickle.load(open("model.pkl","rb"))
firebaseConfig={'apiKey': "AIzaSyC24uvyXxuMzw_96-SlMk_BEximuUmUTPY",
  'authDomain': "uvauthentication.firebaseapp.com",
  'projectId': "uvauthentication",
  'storageBucket': "uvauthentication.appspot.com",
  'messagingSenderId': "577551314847",
  'appId': "1:577551314847:web:b299a19e71e175a6d997aa",
  'measurementId': "G-5J6SK3JJ17",
  'databaseURL':""
}
firebase=pyrebase.initialize_app(firebaseConfig)
auth=firebase.auth()
storage=firebase.storage()
firebaseConfig1={
  'apiKey': "AIzaSyBWW3MflR1E_duhKdz-6TD5PQnp6YQmWz0",
  'authDomain': "staff-details-495df.firebaseapp.com",
  'projectId': "staff-details-495df",
  'storageBucket': "staff-details-495df.appspot.com",
  'messagingSenderId': "750490829584",
  'appId': "1:750490829584:web:b85fc2a3c27200cf98db95",
  'measurementId': "G-W4V7K08HL8",
  'databaseURL':""
}
firebase1=pyrebase.initialize_app(firebaseConfig1)
auth1=firebase1.auth()
l=[]
roll=[]
year=[]
depa=[]
lat=[]
lon=[]
status=[]

@app.route("/")

def homepage():
    return render_template("home.html")

@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/student")
def student():
    return render_template("student.html")

@app.route("/faculty")
def faculty():
    return render_template("faculty.html")

@app.route("/stdsignup",methods=["POST","GET"])
def stdsignup():
    k=[i for i in request.form.values()]
    email=k[0].lower()
    password=k[1]
    try:
        auth.create_user_with_email_and_password(email,password)
        return render_template("student.html")
    except:
        return render_template("student.html",msg="Email Already Exists")
@app.route("/facsignup",methods=["POST","GET"])
def facsignup():
    k=[i for i in request.form.values()]
    email=k[0].lower()
    password=k[1]
    try:
        auth1.create_user_with_email_and_password(email,password)
        return render_template("faculty.html")
    except:
        return render_template("faculty.html",msg="Email Already Exists")

@app.route("/facsignin",methods=["POST","GET"])
def facsignin():
    fval=[i for i in request.form.values()]
    email=fval[0].lower()
    password=fval[1]
    try:
        auth1.sign_in_with_email_and_password(email,password)
    except:
        return render_template("faculty.html",msg="Invalid User or Incorrect Password")
    return render_template("facultyform.html")

@app.route("/create",methods=["POST","GET"])
def create():
    val=[i for i in request.form.values()]
    print(val)
    for i in val:
        l.append(i)
    remsg="Class Room Scheduled"
    return render_template("facultyform.html",remsg=remsg)

@app.route("/studentform",methods=["POST","GET"])

def studentform():
    sval=[i for i in request.form.values()]
    email=sval[0].lower()
    password=sval[1]
    k=l
    if len(k)==0:
      return render_template("student.html",msg="No Class Scheduled Yet")
    course=k[1]
    rmn=k[-1]
    try:
        auth.sign_in_with_email_and_password(email,password)
    except:
        return render_template("student.html",msg="Invalid User or Incorrect Password")
    return render_template("studentform.html",rm=rmn,course="Attendance for {} class".format(course))

@app.route("/predict",methods=["POST","GET"])

def predict():
    vals=[i for i in request.form.values()]
    print(vals)
    roll.append(vals[0])
    year.append(vals[1])
    depa.append(vals[2])
    room=int(vals[3])
    lat.append(vals[-2])
    lon.append(vals[-1])
    l1=float(str(vals[-2])[0:10])
    lo1=float(str(vals[-1])[0:10])
    mark=model.predict([[l1,lo1,room],])[0]
    print(mark)
    if mark==0:
        marked="Absent"
        status.append(marked)
    else:
        marked="Present"
        status.append(marked)
    return render_template("studentform.html",attend="Your attendence marked as: "+marked)

@app.route("/download",methods=["POST","GET"])

def download():
    df1=pd.DataFrame({"ROLL_NO":roll,"Year":year,"Department":depa,"status":status})
    if df1.shape[0]==0:
        return render_template("facultyform.html",msg="No Presenters Yet")
    resp=make_response(df1.to_csv(index=False))
    resp.headers["Content-Disposition"]="attachement;filename=attend_sheet.csv"
    resp.headers["Content-Type"]="text/csv"
    lat.clear()
    lon.clear()
    year.clear()
    depa.clear()
    roll.clear()
    l.clear()
    status.clear()
    return resp
if __name__=='__main__':
    app.run(debug=True)
