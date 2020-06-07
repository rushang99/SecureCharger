import sqlite3
import random
import string
import sys
conn = sqlite3.connect('cars.db')
conn.execute('UPDATE users SET lock= 0')
conn.execute('UPDATE users SET balance = 15000')
conn.commit()
conn.close()