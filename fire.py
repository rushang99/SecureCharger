import pyrebase
config = {
    "apiKey": "AIzaSyAGas29t240FwqdvXjdwzz4kITTN2Ix1ro",
    "authDomain": "charger-1eb48.firebaseapp.com",
    "databaseURL": "https://charger-1eb48.firebaseio.com",
    "projectId": "charger-1eb48",
    "storageBucket": "charger-1eb48.appspot.com",
    "messagingSenderId": "430093083458",
    "serviceAccount": "/home/raghav/SecureCharger/secure.json"
}
 
firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
email = "guptaraghav1999@gmail.com"
password = "12345678"
user = auth.sign_in_with_email_and_password(email,password)


 
# Get a reference to the database service
db = firebase.database()
 
# #retrieve Value
# users = db.child("users").get()
# print(users.val())
 
# #retrieve key
# user = db.child("users").get()
# print(user.key())
 
#retrieve each
all_users = db.child("Users").get()
for user in all_users.each():
    print(user.key())
    print(user.val()['chargingCost'])

# data = {
#     "name": "Mortimer 'Morty' Smith",
#     "id": "1234567"
# }
 
# # Pass the user's idToken to the push method
# results = db.child("users").push(data, user['idToken'])