import sqlite3
import random
import string
import sys
import json

num_cars = int(sys.argv[1])
conn = sqlite3.connect('cars.db')
conn.execute('''CREATE TABLE USERS
         (NAME          TEXT  PRIMARY KEY  NOT NULL,
         BALANCE            INT     NOT NULL,
         LOCK        INT NOT NULL);''')

for i in range(0, num_cars):
    amount  = random.randint(100, 500)
    letters = string.ascii_letters
    name = ''.join(random.choice(letters) for i in range(random.randint(3,10)))
    Model = ''.join(random.choice(letters) for i in range(random.randint(2,10)))
    Vendor = ''.join(random.choice(letters) for i in range(random.randint(1,9)))
    conn.execute("INSERT INTO USERS (NAME,BALANCE,LOCK) \
        VALUES ('"  + name +"', "+ str(amount*15)+", 0)")

    dictionary ={ 
        "Model":Model,
        "Vendor":Vendor,
        "Id":name,
        "Amount":str(amount),
        "Cert":""
    }      
    json_object = json.dumps(dictionary, indent = 4) 
    with open("cars/car" + str(i)+".json", "w") as outfile: 
        outfile.write(json_object) 

conn.commit()
conn.close()

