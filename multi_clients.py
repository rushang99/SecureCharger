from subprocess import Popen

num=1
for i in range(0, num):
    # call(["python", "client.py", "car" + str(i)+ ".json"])
    # call(['gnome-terminal', '-e', "python ocpp_client.py car" + str(i) +".json"])
    Popen(["python3", "client.py", "car" + str(i)+ ".json"])
