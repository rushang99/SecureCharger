from subprocess import Popen
for i in range(0, 100):
    # call(["python", "client.py", "car" + str(i)+ ".json"])
    # call(['gnome-terminal', '-e', "python ocpp_client.py car" + str(i) +".json"])
    Popen(["python", "client.py", "car" + str(i)+ ".json"])