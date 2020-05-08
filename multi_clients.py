from subprocess import call 
from subprocess import Popen
for i in range(0, 100):
    # call(["python", "ocpp_client.py", "car" + str(i)+ ".json"])
    # call(['gnome-terminal', '-e', "python ocpp_client.py car" + str(i) +".json"])
    Popen(["python3", "client.py", "car" + str(i)+ ".json"])
