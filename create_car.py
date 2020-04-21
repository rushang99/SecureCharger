import json
import random
import string
import pyrebase
import pem


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


amount  = random.randint(100, 500)
letters = string.ascii_letters
Model = ''.join(random.choice(letters) for i in range(random.randint(1,9)))
Vendor = ''.join(random.choice(letters) for i in range(random.randint(1,9)))
Id = ''.join(random.choice(letters) for i in range(random.randint(1,9)))
db.child("Users").child(Id).set({"chargingCost":str(amount), "userLock" : False}) 

# Data to be written
dictionary ={ 
    "Model":Model,
	"Vendor":Vendor,
	"Id":Id,
	"Amount":str(amount),
	"Cert":""
} 
  
# Serializing json  
json_object = json.dumps(dictionary, indent = 4) 
  
# Writing to sample.json 
with open("sample.json", "w") as outfile: 
    outfile.write(json_object) 
