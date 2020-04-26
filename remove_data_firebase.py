import json
import random
import string
import pyrebase
import pem
import os

path, dirs, files = next(os.walk("cars"))
file_count = len(files)

config = {
    "apiKey": "AIzaSyAGas29t240FwqdvXjdwzz4kITTN2Ix1ro",
    "authDomain": "charger-1eb48.firebaseapp.com",
    "databaseURL": "https://charger-1eb48.firebaseio.com",
    "projectId": "charger-1eb48",
    "storageBucket": "charger-1eb48.appspot.com",
    "messagingSenderId": "430093083458",
    # "serviceAccount": "/home/raghav/SecureCharger/secure.json"
    "serviceAccount": "/home/rushang99/Downloads/SecureCharger/secure.json"
}
firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
email = "guptaraghav1999@gmail.com"
password = "12345678"
user = auth.sign_in_with_email_and_password(email,password)
db = firebase.database()

for i in range(0, file_count):
    f = open("cars/car"+str(i)+".json",'r')
    data = json.load(f)
    name = data["Id"]
    db.child("Users").child(name).remove()
